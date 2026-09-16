<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — n1-outstanding-384

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `c576dae8d`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/h11/n1-outstanding-384` · **Registry status**: active · **Purpose**: not supplied

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `n1-outstanding-384` |
| Directory | `outputs/h11/n1-outstanding-384` |
| Registry status | active |
| Purpose | not supplied |
| Run type (derived) | mixed |
| Primary hypothesis | H11 |
| Also informs | — |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `Era 2` |
| Working-notes Obs | — |
| Registry notes | H11 (n=1 outstanding, 384px). NB the four pro-\* anti-diagonal pools dispatched as Flash, not Pro (E57 billing verdict); genuine-Pro re-dispatch is run n1-pro-rerun-384. |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 384 |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | era-2-487 |
| Test tiles | 487 |
| Bounds | `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` |
| Calibration set id | cal-20-384 |
| Calibration tiles | 20 |

## 3. Execution — passes on file

### 3.1 Proposer passes (17)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `brief-text-t03` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.3 | ok | 487 | 487 | 0 |
| `brief-text-t03` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.3 | ok | 487 | 487 | 0 |
| `brief-text-t03` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.3 | ok | 487 | 487 | 0 |
| `image-t0` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.0 | ok | 487 | 487 | 0 |
| `image-t0` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.0 | ok | 487 | 487 | 0 |
| `image-t0` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.0 | ok | 487 | 487 | 0 |
| `image-t03` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.3 | ok | 487 | 487 | 0 |
| `image-t03` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.3 | ok | 487 | 487 | 0 |
| `image-t03` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.3 | ok | 487 | 487 | 0 |
| `pro-image-high-t0` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.0 | partial | 486 | 487 | 251 |
| `pro-image-high-t0` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.0 | partial | 486 | 487 | 285 |
| `pro-image-high-t0` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.0 | partial | 485 | 487 | 287 |
| `pro-image-medium-t07` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | medium | 0.7 | ok | 487 | 487 | 14 |
| `pro-text-high-t0` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.0 | partial | 485 | 487 | 663 |
| `pro-text-high-t0` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.0 | partial | 485 | 487 | 643 |
| `pro-text-high-t0` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.0 | partial | 485 | 487 | 623 |
| `pro-text-medium-t07` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | medium | 0.7 | ok | 487 | 487 | 50 |

### 3.2 Verifier passes (1)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `image-t0-verified-v1-n3` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 690 | 0 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 18 |
| Input tokens (billed) | 82,614,626 |
| Input tokens (cached) | 70,853,630 |
| Output tokens | 1,186,300 |
| Thinking tokens | 12,093,779 |
| Total tokens | 95,894,705 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$44.8662 over 18 of 18 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 3.47 h over 18 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (48)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `baseline-flash-image-minimal-t-0-0-487-tiles` | single-pass | none | 1 | — | not supplied | 0.5984 [0.5580, 0.6391] | 0.6802 [0.6423, 0.7155] | 0.3136 |
| `baseline-flash-image-minimal-t-0-3` | single-pass | none | 1 | — | not supplied | 0.5931 [0.5518, 0.6351] | 0.6770 [0.6392, 0.7130] | 0.3053 |
| `baseline-flash-text-minimal-t-0-3` | single-pass | none | 1 | — | not supplied | 0.4992 [0.4426, 0.5558] | 0.5231 [0.4647, 0.5801] | 0.0392 |
| `baseline-pro-image-high-t-0-0` | single-pass | none | 1 | — | not supplied | 0.5276 [0.4798, 0.5734] | 0.6337 [0.5860, 0.6769] | 0.6062 |
| `baseline-pro-image-high-t-0-0-post-e71` | single-pass | none | 1 | — | not supplied | 0.5446 [0.5009, 0.5876] | 0.6656 [0.6237, 0.7049] | 0.6481 |
| `baseline-pro-image-medium-t-0-7` | single-pass | none | 1 | — | 941 | 0.4520 [0.4032, 0.4985] | 0.5858 [0.5307, 0.6347] | 0.5984 |
| `baseline-pro-text-high-t-0-0` | single-pass | none | 1 | — | not supplied | 0.4942 [0.4384, 0.5478] | 0.5249 [0.4679, 0.5794] | 0.3808 |
| `baseline-pro-text-high-t-0-0-post-e71` | single-pass | none | 1 | — | not supplied | 0.4919 [0.4378, 0.5452] | 0.5208 [0.4651, 0.5746] | 0.3992 |
| `baseline-pro-text-medium-t-0-7` | single-pass | none | 1 | — | 1445 | 0.4160 [0.3613, 0.4712] | 0.4298 [0.3740, 0.4863] | 0.3105 |
| `brief-text-t03-consensus-1of3` | consensus | consensus | 3 | k=1 | 1229 | 0.4663 [0.4085, 0.5255] | 0.4808 [0.4228, 0.5415] | 0.0651 |
| `brief-text-t03-consensus-2of3` | consensus | consensus | 3 | k=2 | 952 | 0.5537 [0.4970, 0.6097] | 0.5725 [0.5134, 0.6277] | 0.0938 |
| `brief-text-t03-consensus-3of3` | consensus | consensus | 3 | k=3 | 794 | 0.5907 [0.5346, 0.6443] | 0.6054 [0.5485, 0.6599] | 0.1711 |
| `brief-text-t03-single-pass-run_1` | single-pass | none | 1 | — | 1078 | 0.5010 [0.4454, 0.5574] | 0.5261 [0.4686, 0.5834] | 0.0427 |
| `brief-text-t03-single-pass-run_2` | single-pass | none | 1 | — | 1052 | 0.4990 [0.4437, 0.5556] | 0.5286 [0.4712, 0.5850] | 0.0143 |
| `brief-text-t03-single-pass-run_3` | single-pass | none | 1 | — | 1096 | 0.4977 [0.4386, 0.5545] | 0.5147 [0.4544, 0.5718] | 0.0605 |
| `image-t0-consensus-1of3` | consensus | consensus | 3 | k=1 | 690 | 0.6240 [0.5816, 0.6661] | 0.7129 [0.6750, 0.7493] | 0.2157 |
| `image-t0-consensus-2of3` | consensus | consensus | 3 | k=2 | 681 | 0.6290 [0.5863, 0.6710] | 0.7186 [0.6808, 0.7549] | 0.2157 |
| `image-t0-consensus-3of3` | consensus | consensus | 3 | k=3 | 675 | 0.6288 [0.5866, 0.6708] | 0.7189 [0.6819, 0.7556] | 0.2197 |
| `image-t0-single-pass-run_1` | single-pass | none | 1 | — | 745 | 0.6000 [0.5596, 0.6408] | 0.6814 [0.6438, 0.7164] | 0.3124 |
| `image-t0-single-pass-run_2` | single-pass | none | 1 | — | 747 | 0.5956 [0.5553, 0.6364] | 0.6785 [0.6404, 0.7142] | 0.3160 |
| `image-t0-single-pass-run_3` | single-pass | none | 1 | — | 746 | 0.5995 [0.5591, 0.6400] | 0.6808 [0.6428, 0.7159] | 0.3124 |
| `image-t03-consensus-1of3` | consensus | consensus | 3 | k=1 | 812 | 0.5822 [0.5395, 0.6270] | 0.6544 [0.6143, 0.6937] | 0.1689 |
| `image-t03-consensus-2of3` | consensus | consensus | 3 | k=2 | 664 | 0.6424 [0.6002, 0.6843] | 0.7261 [0.6894, 0.7622] | 0.2216 |
| `image-t03-consensus-3of3` | consensus | consensus | 3 | k=3 | 567 | 0.6766 [0.6340, 0.7194] | 0.7525 [0.7157, 0.7879] | 0.3489 |
| `image-t03-single-pass-run_1` | single-pass | none | 1 | — | 753 | 0.5943 [0.5534, 0.6364] | 0.6751 [0.6377, 0.7106] | 0.3065 |
| `image-t03-single-pass-run_2` | single-pass | none | 1 | — | 746 | 0.5944 [0.5512, 0.6395] | 0.6757 [0.6363, 0.7130] | 0.2934 |
| `image-t03-single-pass-run_3` | single-pass | none | 1 | — | 747 | 0.5905 [0.5508, 0.6294] | 0.6802 [0.6436, 0.7154] | 0.3160 |
| `pro-image-high-t0-consensus-1of3` | consensus | consensus | 3 | k=1 | 730 | 0.5614 [0.5176, 0.6033] | 0.6747 [0.6317, 0.7152] | 0.5577 |
| `pro-image-high-t0-consensus-2of3` | consensus | consensus | 3 | k=2 | 690 | 0.5760 [0.5326, 0.6176] | 0.6987 [0.6563, 0.7368] | 0.5678 |
| `pro-image-high-t0-consensus-3of3` | consensus | consensus | 3 | k=3 | 648 | 0.5854 [0.5401, 0.6282] | 0.7073 [0.6641, 0.7458] | 0.5921 |
| `pro-image-high-t0-single-pass-run_1` | single-pass | none | 1 | — | 692 | 0.5288 [0.4818, 0.5745] | 0.6371 [0.5897, 0.6802] | 0.6093 |
| `pro-image-high-t0-single-pass-run_1-post-e71` | single-pass | none | 1 | — | 750 | 0.5401 [0.4970, 0.5827] | 0.6650 [0.6235, 0.7041] | 0.6508 |
| `pro-image-high-t0-single-pass-run_2` | single-pass | none | 1 | — | 681 | 0.5305 [0.4829, 0.5760] | 0.6344 [0.5868, 0.6772] | 0.6073 |
| `pro-image-high-t0-single-pass-run_2-post-e71` | single-pass | none | 1 | — | 744 | 0.5479 [0.5041, 0.5912] | 0.6667 [0.6255, 0.7061] | 0.6508 |
| `pro-image-high-t0-single-pass-run_3` | single-pass | none | 1 | — | 677 | 0.5234 [0.4748, 0.5696] | 0.6295 [0.5815, 0.6733] | 0.6021 |
| `pro-image-high-t0-single-pass-run_3-post-e71` | single-pass | none | 1 | — | 741 | 0.5459 [0.5017, 0.5888] | 0.6650 [0.6222, 0.7045] | 0.6428 |
| `pro-image-medium-t07-single-pass-run_1` | single-pass | none | 1 | — | 941 | 0.4520 [0.4032, 0.4985] | 0.5858 [0.5307, 0.6347] | 0.5984 |
| `pro-text-high-t0-consensus-1of3` | consensus | consensus | 3 | k=1 | 1192 | 0.4634 [0.4092, 0.5167] | 0.4929 [0.4363, 0.5476] | 0.2629 |
| `pro-text-high-t0-consensus-2of3` | consensus | consensus | 3 | k=2 | 991 | 0.5203 [0.4649, 0.5736] | 0.5526 [0.4958, 0.6057] | 0.3333 |
| `pro-text-high-t0-consensus-3of3` | consensus | consensus | 3 | k=3 | 842 | 0.5748 [0.5212, 0.6281] | 0.6092 [0.5550, 0.6615] | 0.3894 |
| `pro-text-high-t0-single-pass-run_1` | single-pass | none | 1 | — | 1026 | 0.5010 [0.4456, 0.5527] | 0.5298 [0.4732, 0.5827] | 0.3916 |
| `pro-text-high-t0-single-pass-run_1-post-e71` | single-pass | none | 1 | — | 1090 | 0.4931 [0.4396, 0.5458] | 0.5207 [0.4655, 0.5738] | 0.3970 |
| `pro-text-high-t0-single-pass-run_2` | single-pass | none | 1 | — | 1028 | 0.4867 [0.4307, 0.5431] | 0.5195 [0.4622, 0.5764] | 0.3704 |
| `pro-text-high-t0-single-pass-run_2-post-e71` | single-pass | none | 1 | — | 1112 | 0.4848 [0.4295, 0.5400] | 0.5145 [0.4582, 0.5709] | 0.3922 |
| `pro-text-high-t0-single-pass-run_3` | single-pass | none | 1 | — | 1004 | 0.4948 [0.4390, 0.5476] | 0.5254 [0.4684, 0.5792] | 0.3805 |
| `pro-text-high-t0-single-pass-run_3-post-e71` | single-pass | none | 1 | — | 1060 | 0.4977 [0.4442, 0.5497] | 0.5271 [0.4717, 0.5790] | 0.4083 |
| `pro-text-medium-t07-single-pass-run_1` | single-pass | none | 1 | — | 1445 | 0.4160 [0.3613, 0.4712] | 0.4298 [0.3740, 0.4863] | 0.3105 |
| `pv-n1-image-t0-n3-opmax` | proposer-verifier | verified | 3 | k=2/pt=0.15 | 446 | 0.7673 [0.7265, 0.8041] | 0.8717 [0.8444, 0.8958] | 0.8397 |

Buffers on file (metres), by how many conditions carry that set:

- 48 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 48 of 48 condition(s).

### 5.1 Condition caveats (1 condition(s), 1 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `pv-n1-image-t0-n3-opmax`
  IN-SAMPLE OPTIMUM (E56 class): the archived per-architecture Era-2 PV board's sweep-optimal cell pv-n1-image-t0-n3 (archived at 005e6c71, retired instrument build\_tiered\_leaderboard.py; archive/superseded-leaderboards/leaderboard/per-architecture/era2/pv/leaderboard\_tiers\_20m.json; materialised from stage image-t0-verified-v1-n3 at the F1@20-argmax (vote\_t 2, prob\_t 0.15) of its sweep on the evaluation set). Registered 2026-09-10 for the GS Era-2 board's symmetry fix (planning/gs-era2-verified-board-2026-09-08.md, changelog 2026-09-10 later): the Gemini 3 family at its sweep-optimal level, beside the 3.7 / 3.8 screen cells which are sweep-best points too. ADMITTED TO THE BOARD 2026-09-12 (PI ruling R3, planning/k-ladder-review-2026-09-11.md § 4): the board takes every verified cell on its frame regardless of K, so this K = 3 cell is a member. Its evaluation is now the board-frame score (era2-b-487); the Era-2-frame score it carried while off-board is kept at results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/era2/n1-outstanding-384\_\_pv-n1-image-t0-n3-opmax/evaluation.json and is the waived opmax/g2 evaluation.

### 5.2 Scope overrides (1 condition(s), 1 distinct frame(s))

These conditions are scored on a frame other than the run's nominal scope in § 2 — the 327-vs-487 leakage trap the verifier exists to catch, disclosed per condition:

- `pv-n1-image-t0-n3-opmax`
  bounds\_path = inputs/vectors/bounds/384/era2\_b\_intersection\_bounds.geojson, calibration\_set\_id = None, n\_calibration\_tiles = None, n\_test\_tiles = 487, test\_set\_id = era2-b-487

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Completeness waivers (2026-09-13, S153 Batch 1 item 2): the six rescore-2026-05-31 consensus\_t{1..3} evaluations of the two pro-\*-high-t0 pools are the PRE-RECOVERY scoring of the same consensus geojsons the registered \*-consensus-{1..3}of3 conditions now score at recovery-reeval-2026-09-08; waived with reasons. The eight pinned-vintage WARNs are left standing as ruling-3a disclosures. No metric changed.

### 5.4 Waived evaluations (24, 8 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **17 evaluation(s)** — not supplied — a bare-string entry, written before the waiver register carried reasons
  - `results/paper-eval/mcc/384px/flash-image-minimal-t-0-0-487-tiles/evaluation.json`
  - `results/paper-eval/mcc/384px/flash-image-minimal-t-0-3/evaluation.json`
  - `results/paper-eval/mcc/384px/flash-text-minimal-t-0-3/evaluation.json`
  - `results/paper-eval/mcc/384px/pro-image-high-t-0-0/evaluation.json`
  - `results/paper-eval/mcc/384px/pro-image-medium-t-0-7/evaluation.json`
  - `results/paper-eval/mcc/384px/pro-text-high-t-0-0/evaluation.json`
  - `results/paper-eval/mcc/384px/pro-text-medium-t-0-7/evaluation.json`
  - `results/paper-eval/n1/384px-all-buffers/flash-image-minimal-t-0-0-487-tiles/evaluation.json`
  - `results/paper-eval/n1/384px-all-buffers/flash-image-minimal-t-0-3/evaluation.json`
  - `results/paper-eval/n1/384px-all-buffers/flash-text-minimal-t-0-3/evaluation.json`
  - `results/paper-eval/n1/384px-all-buffers/pro-image-high-t-0-0/evaluation.json`
  - `results/paper-eval/n1/384px-all-buffers/pro-image-medium-t-0-7/evaluation.json`
  - … and 5 more under the same waiver (full list in `results/run-conditions.json`, this run's `_ignored_evals`)
- **1 evaluation(s)** — GS Era-2 board symmetry fix (planning/gs-era2-verified-board-2026-09-08.md): pv-n1-image-t0-n3-opmax's archived geojson re-scored on the Era-2 frame with a 200-draw bootstrap to prove the archived F1 reproduces; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/g2/n1-outstanding-384__pv-n1-image-t0-n3-opmax/evaluation.json`
- **1 evaluation(s)** — Superseded pre-recovery scoring. This 2026-05-31 rescore scored outputs/h11/n1-outstanding-384/pro-image-high-t0/consensus/consensus\_t1.geojson — the same detections the registered condition pro-image-high-t0-consensus-1of3 now scores at results/recovery-reeval-2026-09-08/n1-outstanding-384/pro-image-high-t0-consensus-1of3/evaluation.json after the E71 dead-tile recovery (99ae28ec4) rewrote the file. Kept as the pre-recovery record per ruling 3a (PI, 2026-09-07); not a second condition.
  - `results/rescore-2026-05-31/n1-outstanding-384/pro-image-high-t0/consensus/consensus_t1/evaluation.json`
- **1 evaluation(s)** — Superseded pre-recovery scoring. This 2026-05-31 rescore scored outputs/h11/n1-outstanding-384/pro-image-high-t0/consensus/consensus\_t2.geojson — the same detections the registered condition pro-image-high-t0-consensus-2of3 now scores at results/recovery-reeval-2026-09-08/n1-outstanding-384/pro-image-high-t0-consensus-2of3/evaluation.json after the E71 dead-tile recovery (99ae28ec4) rewrote the file. Kept as the pre-recovery record per ruling 3a (PI, 2026-09-07); not a second condition.
  - `results/rescore-2026-05-31/n1-outstanding-384/pro-image-high-t0/consensus/consensus_t2/evaluation.json`
- **1 evaluation(s)** — Superseded pre-recovery scoring. This 2026-05-31 rescore scored outputs/h11/n1-outstanding-384/pro-image-high-t0/consensus/consensus\_t3.geojson — the same detections the registered condition pro-image-high-t0-consensus-3of3 now scores at results/recovery-reeval-2026-09-08/n1-outstanding-384/pro-image-high-t0-consensus-3of3/evaluation.json after the E71 dead-tile recovery (99ae28ec4) rewrote the file. Kept as the pre-recovery record per ruling 3a (PI, 2026-09-07); not a second condition.
  - `results/rescore-2026-05-31/n1-outstanding-384/pro-image-high-t0/consensus/consensus_t3/evaluation.json`
- **1 evaluation(s)** — Superseded pre-recovery scoring. This 2026-05-31 rescore scored outputs/h11/n1-outstanding-384/pro-text-high-t0/consensus/consensus\_t1.geojson — the same detections the registered condition pro-text-high-t0-consensus-1of3 now scores at results/recovery-reeval-2026-09-08/n1-outstanding-384/pro-text-high-t0-consensus-1of3/evaluation.json after the E71 dead-tile recovery (99ae28ec4) rewrote the file. Kept as the pre-recovery record per ruling 3a (PI, 2026-09-07); not a second condition.
  - `results/rescore-2026-05-31/n1-outstanding-384/pro-text-high-t0/consensus/consensus_t1/evaluation.json`
- **1 evaluation(s)** — Superseded pre-recovery scoring. This 2026-05-31 rescore scored outputs/h11/n1-outstanding-384/pro-text-high-t0/consensus/consensus\_t2.geojson — the same detections the registered condition pro-text-high-t0-consensus-2of3 now scores at results/recovery-reeval-2026-09-08/n1-outstanding-384/pro-text-high-t0-consensus-2of3/evaluation.json after the E71 dead-tile recovery (99ae28ec4) rewrote the file. Kept as the pre-recovery record per ruling 3a (PI, 2026-09-07); not a second condition.
  - `results/rescore-2026-05-31/n1-outstanding-384/pro-text-high-t0/consensus/consensus_t2/evaluation.json`
- **1 evaluation(s)** — Superseded pre-recovery scoring. This 2026-05-31 rescore scored outputs/h11/n1-outstanding-384/pro-text-high-t0/consensus/consensus\_t3.geojson — the same detections the registered condition pro-text-high-t0-consensus-3of3 now scores at results/recovery-reeval-2026-09-08/n1-outstanding-384/pro-text-high-t0-consensus-3of3/evaluation.json after the E71 dead-tile recovery (99ae28ec4) rewrote the file. Kept as the pre-recovery record per ruling 3a (PI, 2026-09-07); not a second condition.
  - `results/rescore-2026-05-31/n1-outstanding-384/pro-text-high-t0/consensus/consensus_t3/evaluation.json`

## 6. Analyses that read this run (7)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `diversity-dividend-384` | 3 of 22 | leaderboard | `H3` | confirmatory-with-deviation | Results | `None for the operating-point selection: the registered H3 analysis plan (osf/preregistration.md:519-521) specifies 'Generate threshold sweep curves', 'Identify optimal (N, threshold)', and 'Compare single-pass mean F1 vs voted F1' against the test tiles, so the best-operating- point characterisation is the preregistered method (not in-sample/E56 -- that rule governs the verifier prob_t diagnostics, a distinct case; see E56 Update 2026-06-06).`, `E49/E51 (T=0.7 production carry-forward temperature; HIGH thinking) -- the characterised configurations, carried forward from Phase 2b.`, `Production operating point reported alongside best: text 4-of-5, image 3-of-5 (the 55maps deployment thresholds); the best-minus-N5 delta is the within-test operating-point sensitivity.` | 2026-06-06T00:07:40Z | `results/diversity-dividend-384` |
| `gs-era2-verified-board-2026-09-10` | 1 of 103 | leaderboard | `H2`, `H1` | post-hoc | Results | — | 2026-09-16T02:58:00Z | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json` |
| `h6-a07-voting-thresholds` | 6 of 6 | sweep | `H6` | post-hoc | Methods | `E74`, `E57`, `E71` | 2026-09-10T06:56:15Z | `results/h6-registered-analyses` |
| `h6-a09-cost-gate` | 2 of 4 | diagnostic | `H6` | post-hoc | Methods | `E74`, `E57`, `E71` | 2026-09-08T01:53:31Z | `results/h6-registered-analyses` |
| `n1-baseline-matrix-384` | 3 of 18 | leaderboard | `H1`, `H7` | post-hoc | Results | `E57` | 2026-06-04T02:05:31Z | `results/paper-eval/n1/384px-14buf-mcc` |
| `null-exemplar-sensitivity-2026-09-13` | 1 of 235 | comparison | — | post-hoc | Appendix | — | not supplied | `results/null-exemplar-sensitivity-2026-09-13/findings.md` |
| `uplift-supplement-flatten` | 48 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |

## 7. Findings documents (1)

| Document | Named by |
|---|---|
| `results/null-exemplar-sensitivity-2026-09-13/findings.md` | `null-exemplar-sensitivity-2026-09-13` |

## 8. Protocol errata

### 8.1 Registered as deviations (6)

Listed in the `deviations` field of an analysis that reads this run:

- **E57** — H11 384px Pro/baseline detection metadata — model template default and output\_dir overrides
- **E71** — `n\_tiles\_processed` manifest column carries two semantics (dispatched vs completed) plus a verifier-row placeholder (GAP-8) — 15 passes with genuine coverage shortfalls, two live conditions carrying dead tiles as artificial false negatives
- **E74** — H6 (Flash→Pro transfer, Phase 4) — registered confirmatory hypothesis never executed; deferral never ratified
- **E49/E51 (T=0.7 production carry-forward temperature; HIGH thinking) -- the characterised configurations, carried forward from Phase 2b.** — not supplied
- **None for the operating-point selection: the registered H3 analysis plan (osf/preregistration.md:519-521) specifies 'Generate threshold sweep curves', 'Identify optimal (N, threshold)', and 'Compare single-pass mean F1 vs voted F1' against the test tiles, so the best-operating- point characterisation is the preregistered method (not in-sample/E56 -- that rule governs the verifier prob_t diagnostics, a distinct case; see E56 Update 2026-06-06).** — not supplied
- **Production operating point reported alongside best: text 4-of-5, image 3-of-5 (the 55maps deployment thresholds); the best-minus-N5 delta is the within-test operating-point sensitivity.** — not supplied

## 9. Documents and structure in the run directory

No `experiment_intent.md`, `evaluation.md`, `pre_launch_audit.md` or retrospective report under this directory.

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `brief-text-t03` | text | `brief-text-t03` |
| `image-t0` | image | `image-t0` |
| `image-t03` | image | `image-t03` |
| `pro-image-high-t0` | image | `pro-image-high-t0` |
| `pro-image-medium-t07` | image | `pro-image-medium-t07` |
| `pro-text-high-t0` | text | `pro-text-high-t0` |
| `pro-text-medium-t07` | text | `pro-text-medium-t07` |

1 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `c576dae8d` |
| Manifest extractor | `0.7.1` |
| Run row last extracted | `2026-09-13T09:02:37Z` |

Inputs:

- `results/run-registry.json`
- `results/runs-manifest.json`
- `results/conditions-manifest.json`
- `results/passes-manifest.json`
- `results/analyses-manifest.json`
- `results/run-conditions.json`
- `results/run-analyses.json`
- `docs/methodology/preregistration/protocol-errata.md`

The run row's own upstream sources, as the manifest records them:

- `results/run-facts.json`
- `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
