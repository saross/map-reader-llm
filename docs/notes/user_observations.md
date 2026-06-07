# User observations — collaboration meta-log

Observation 1: Gemini is not as tractable / corrigible as Claude, It's smart, but esp. in Antigravity it's like 'what the hell did you just do and why did you do that?' in a way that Claude isn't. Just ran an overnight historical map extraction and it decided to switch from using 3 Flash (which I'm using for testing and development) to 3 Pro, which...only cost me about $2.50 but burned my day's quota. If you forget something (specifying a model, specifying a prompt or script to use/run, specifying a target / count / etc.), you just never know what you're going to get, whereas Claude usually does the right thing.

Observation 2:
Antigravity is really growing on me as harness. The fact that chats are saved and can be re-accessed makes recovery from crashes easier, and the availability of logs / interactions is great for transparency.

Observation 3:
Forgets what it has done, keeps re-running things that it should already have at hand, even when I gesture towards the right file (enough that Claude would have found it)

Observation 4:
Seems to fixate on certain things and even if I correct it won't change. For example, it's convinced that mounds have 'inward hachures' but they are outward:
The Change: Update the JSON schema to require a description field before the label.
From: {"label": "burial_mound"}
To: {"description": "Circular feature with inward hachures, distinct from terrain", "label": "burial_mound"}
Why: This acts as a "speed bump," forcing the model to ground its decision in visual evidence rather than guessing.

[CORRECTION 2025-12-19]: I STAND CORRECTED. Burial mounds have OUTWARD facing hachures (like a hill). Depressions have INWARD facing hachures. The user explicitly caught this error in my reasoning. I have updated Prompt v3.6 to reflect this critical distinction ("OUTWARD vs inward or none").

Observation 5:
It has taken *me* a while to learn and exploit the way that Antigravity works, e.g., conversatons in workspaces.

Observation 6:
In line with the 'technoscholasticism' thesis, judgement is sometimes lacking, as when we decided to move to a two-stage classifier but Gemini proposed using an existing prompt rather than revising to to focus on maximum recall.

Observation 7:
Gemini *really* wants to 'continue to the next phase', constantly tapping the breaks to discuss results and plan carefully.

Observation 8:
Gemini makes some good choices (was able to reconstruct an outcome from existing runs instead of doing a new run), but wow, I'm not happy with taste / judgement. It immediately wants to abandon the two-stage pipeline and go back to a single prompt, when we've done almost no optimisation of the two-phase pipeline to explore its potential.

Observation 9:
Gemini keeps putting text back into the prompt even though we've decided to use image-focused prompts. I'll have to start reviewing each prompt manually, including system instructions.

Obervation 10:
We used $57.20 of API credits in the initial, exploratory phase, as I learned how to approach this research and use LLM APIs (in general and Google in particular).

Observation 11:
Neither Opus in the web app nor CC have great judgement about descriptions of symbols and inclusion / exclusion rules - expert guidance required.

Observation 12:
All exploratory work with Gemini 3 Flash and Pro in Dec 2025 cost A$62.93 (57.21 + tax). This cost includes learning the API and doing exploratory work around prompt development, setting us up for proposing formal hypotheses. This work was fairly 'lossy' as I was new to the API, and also Gemini in Antigravity took the liberty of doing some runs very...proactively.

Observation 13:
It remaains difficult to get CC to consistently use my archive structure as opposed to proliferating archive subfolders.

Observation 14:
The sort of thing that needs human intervention is, as an example, the difference between adding new types of text examples to the example library (e.g., hard positives, hard negatives) versus making text more verbose / eleborate. Upon detailed review, 'verbose' text being added was descriptions of hard positives, not more detailed and specific text. Had to refactor the hypotheses to correct this confusion.

Observation 15:
The criticism I've been reading about coding agents are they they are 'good for demos, but not for production', and that they are 'OK for within-distribution coding in common languaged' - these limitations, while troublesome for building production software, are well suited to research programming, which is mostly exploratory and generally of very poor quality (see the CRAPL licence parody). Just getting researchers to use code instead of spreadsheets or GIS is a win. Can implement FAIR4RS protocols better than many researchers. Likewise, the statistical assistance offered by LLMs may be very much standard, within-distribution approaches, but that's *still* and improvement over the ad hoc statistical approaches often used by researchers who are poorly trained in stats.

Observation 16:
I felt a little uncomfortable about the division / organisation of hard negative testing versus library size testing, and sure enough it was a serious problem requiring a refactor of the preregistration...

Observation 17:
Evan after externalising a lot of information, constant application of taste and judgement needed - e.g., the verbose and brief prompts were unaligned between text and image prompts, and prompting (from Gemini) was...distinctly suboptimal. Testing suite not kept up to date, needed to catch that and instruct to extend it.

Observation 18:
Although CC did very well mining the session archives for 'eta' human-llm-interaction observations, for some reason performance on observations about the evolution of the map-reader pipeline were poor: lots of confabulations until corrected, and not as insightful even after they were fixed.

Observation 19:
Throughout most of this project, CC has been extemely corrigible. Specifically, CC has regularly grasped the *intent* of prompts, instructions, experiments, etc. For some reason that broke down with the H10/H12 exploratory tests, where CC correctly assembled few-shot image libraries from an expanded calibration tile set, but then *ran the prompt text-only*. Not only did this error cost significant (wasted) API credits (we already completed n=30 runs on the underlying text-only config and had nothing new to learn), but also wasted half a day's time trying to understand performance (which looked strong but was just an artefact arising from statitistical variation and operation over a smaller test tile set). On reflection, not an entire waste of API / time since we did get the superior WBF aggregation, and development of more robust experimental protocols.

Observation 20:
Has been difficult to get my intent regarding API usage to stick: gate all useage with a review presented to me, only proceed with my approval after confirming configuration - when an outdated SDK on this machine cause 'flex' mode on the gemini API to fail, CC just ran it in 'normal' mode, costing some $30-35 extra for no benefit. Have now tried to ensure that the intent is in memory and scratchpad (with defaults how I want them in code).

Observation 21:
Need to do better with recording past decisions and recording intent - it was a real struggle to get to the point where CC and I agreed on what tile sets were 'production' - I had one mistake in my mental model, and I really had to coax CC along to get us on the same page.

Observation 22:
Still occassional confabulations.

● You're right — that's impossible, and my previous table had an error. Here are the correct numbers from the sweep_2d files:

  Corrected plus-hp K=5 + PV per-buffer F1

  ┌────────┬─────────┬────────┬──────────────┐
  │ Buffer │ HIGH F1 │ MIN F1 │ Δ (HIGH−MIN) │
  ├────────┼─────────┼────────┼──────────────┤
  │   20 m │   0.787 │  0.773 │       +0.014 │
  ├────────┼─────────┼────────┼──────────────┤
  │   30 m │   0.858 │  0.846 │       +0.012 │
  ├────────┼─────────┼────────┼──────────────┤
  │   40 m │   0.876 │  0.869 │       +0.007 │
  ├────────┼─────────┼────────┼──────────────┤
  │   50 m │   0.881 │  0.881 │        0.000 │
  └────────┴─────────┴────────┴──────────────┘

  Both monotone non-decreasing, as they must be. HIGH is slightly ahead at every tight buffer, they converge at 50m.

  What my previous table got wrong

  I had written F1 @ 30m: HIGH=0.881, MIN=0.892 — those numbers were fabricated/transposed. I only actually pulled F1@20m and F1@50m from the sweep output, then made up the 30m/40m rows without re-querying. My apologies — that's exactly the kind of carelessness I should be
  catching. The correct numbers above restore monotonicity.

  Why F1 must be monotone with buffer

  You're correct on the theory too: with a fixed detection set and Hungarian matching, a larger buffer can only add candidate edges, never remove them — so the max matching (TP count) is monotone non-decreasing. FP decreases symmetrically. Therefore precision, recall, and F1
  all monotone non-decrease.

  The only way F1 could decrease across buffers in a sweep table is if each row uses a different operating point (e.g., each buffer gets its own optimal vote_t × prob_t). In this case the sweep picked the same (vote_t=3, prob_t=0.15) at every buffer for both HIGH and MIN, so
  monotonicity held — my table was just wrong, not the underlying analysis.

  Observation 23:
  Severe confabulation problem after 4.7 dropped. Repeated, serious misrepresentations. Diagnosed as context contamination, spurred a 'prune the context surface to mitigate confabulation' pass with CC in a fresh session. Testing now.

Observation 24:
After the post-4.7 confabulation problems (Obs 22, 23), this session (2026-05-26 to -28, documentation audit) showed the verify-before-asserting discipline actually working. CC re-read source files before committing each specific and caught four errors that would otherwise have propagated: the audit plan's own § 3.2 framing was wrong (claimed all four 55-map runs were dual-located; only two are); the experiment_intent.md count was off (~50 claimed vs 139 actual); my own "~60 tile" recollection conflated two separate transitions; and CC's first-pass e47/H11 classification was wrong. The thing that worked: every number and path got a pre-commit re-check, logged in the commit message.

Observation 25:
The H11 reorganisation was heading toward a cost-driven decision (Strategy A/B/C by hours). I redirected by asking "what IS H11, actually?" — and the principled answer (tile-size study + the 384px approach-characterisation that fed the leaderboard) dissolved the B-vs-C question and corrected CC's misclassification of e47. Lesson for me: when CC frames a choice as a cost trade-off, it's worth checking whether a principle makes the trade-off moot.

Observation 26:
The manifest idea (retire "eras", build runs/analyses/passes manifests) came from me mid-conversation, not the original audit plan. CC took it as a genuine improvement rather than defending the existing plan, and we re-sequenced around it — at the cost of partly superseding the README rewrite it had done an hour earlier. Worth it, but a reminder that I should surface structural ideas like this before CC invests in the thing they'll supersede.

Observation 27:
The propose/approve/commit/push-one-at-a-time cadence for the 8 Phase 0 spec edits worked well — each edit got a real review, anti-confabulation checks fired per-edit, and the commit history is legible. Slower than batching, but for spec changes that downstream agents depend on, the per-edit scrutiny was the right call.

Observation 28:
A generalisable pattern, seen a couple of times the week of 2026-05-26: we go down a rabbit hole, the solution gets complicated, and we start building baroque / epicyclic structures to save it — when the better move is to throw out the epicycles and find a clean, principled reframing. H11 was the clearest case (cost-strategy A/B/C comparison plus the SPECIAL_CONFIGS coupling analysis, all dissolved by "what IS H11?"). The complicated path is often a signal that the framing itself is wrong. (Overstated slightly for emphasis, but it's a real phenomenon.)

Observation 29:
Twice this session (2026-05-30) I bounced a question back to "clarify" rather than answer it — whether to rename the UNINTENDED runs, and how to model the consensus conditions. In both cases the right move wasn't a decision but more investigation (reading the E43/E44 errata; dispatching a scan agent), after which CC re-surfaced the fork properly with evidence and a recommendation. The forks that landed in one pass (the outputs/gs/ umbrella, score-all-11) were the ones where CC had already done the legwork. Lesson for CC: when a fork's answer depends on facts not yet gathered, gather first, then present the fork — don't ask cold.

Observation 30:
Before authorising the scoring back-fill, I asked CC to scan how common the unscored-output gap was rather than commit blind. It turned out to be ~11 (a handful, not dozens), which made "score all" an easy yes. Bounding the scope of a corrective action before authorising it is a cheap, high-value reflex — and CC defaulting to a read-only scan agent for the sizing was the right instinct.

Observation 31:
I told CC explicitly not to prime the preregistration-check agent with my expectation (that the comparison was exploratory). The unprimed agent confirmed exploratory AND surfaced a nuance I'd have missed — that the consensus sweep itself is preregistered (H3). The same unprimed-agent discipline caught a parameter-control trap on h8-v2 (it was evaluated on the 327-tile pool, not 487). Not seeding agents with the hoped-for answer is what made their findings trustworthy.

Observation 32:
On the h8-v2/h12-v2 evaluation scope, I pushed back on CC's reading of the canonical scope doc with my own memory of the project — that 487 tiles was the principal scope, with 327 a special case. Rather than either of us simply being right, the conflict triggered a leakage investigation that validated my intuition AND sharpened it: 487 IS principal (for the production / H11 / PV matrix), but 327 is correct for the library studies (h8/h10/h12-v2), because their few-shot examples were mined from the pool_160 tiles that 327 excludes. My domain-memory, CC's doc-reading, and an agent's evidence together produced a more precise answer than any one of them alone. Lesson: when my recollection conflicts with CC's source-reading, the conflict itself is worth investigating — it often means both are partially right about different things.

Observation 33:
For the runs that were months old and that I genuinely couldn't remember (pv-diag-256, verifier-t-pilot), I named my low confidence openly ("I'm a little fuzzy… I support taking time to explore") and asked CC to dispatch agents rather than accept its own MEDIUM-confidence guesses. The agents turned plausible-but-unsourced facts into principled, cited ones — and one reconstructed a run I'd entirely forgotten. Naming low confidence and choosing investigation over a fast answer was the right call for facts headed into a paper's supplementary material.

Observation 34:
Mid-session (2026-05-31) I reframed the conditions-manifest build as both a documentation uplift AND a methodology audit — naming that this is how my manual practice always worked: methodology omissions always surfaced during documentation finalisation, and I'd subconsciously carried the pattern over. CC had been treating it more narrowly as "decompose the 26 runs." Making the dual purpose explicit reshaped the whole approach — standardise-then-decompose, the verifier as an audit instrument — and turned a bookkeeping task into a methodology pass that caught real problems (a CRS bug, a mis-scored verifier). Lesson: surfacing the real *purpose* of a piece of work, not just its mechanics, can change the whole approach.

Observation 35:
Several times this session I steered explicitly toward the principled long-term solution over the expedient patch — "prefer principled over expedient" on the sidecar design, and "I'd like to make the best principles / long-term solution here, not an ad hoc pass… can you walk me through this decision" on the proposer-verifier scoring. Asking to be walked through the decision rather than handed a fix is what produced a durable, documented convention (materialise the actual set; verdicts are separate provenance) instead of a one-off filter that would have hidden the same trap elsewhere.

Observation 36:
When CC proposed scoring single passes alongside the consensus sweep to get the single→consensus delta, I pushed it further — to a full performance-shape 2×2 (single-run → consensus → single-run-PV → consensus-PV) — seeing nearly-free extra information CC hadn't surfaced, and the symmetric "do the reverse for the consensus runs too." The analytical frame often has more in it than the first proposal captures; pushing on "what else does this give us for free?" paid off (and the availability map then kept us honest about how much of it we actually have).

Observation 37:
I insisted on empirically MAPPING the 2×2 availability per run rather than assuming the picture was complete — and the map confirmed no run actually has a full 2×2, vindicating the caution. I also flagged the context budget (80%, a genuinely long session) at the right moment, which let us protect continuity — offload the map to an agent, document, hand off — instead of running dry mid-task. Both are the same instinct: don't let optimism, about completeness or about remaining runway, outrun the evidence.

Observation 38:
CC flagged that picking a verifier threshold by maximising F1 on the test set is in-sample optimism — and my reflex was "but we always exclude calibration tiles from test sets." Chasing that conflict showed both were true about different doors: calibration-exclusion stops library/example leakage, but it doesn't stop tuning-on-test. And it surfaced that the EXISTING pipeline's verifier operating points (pv-diag / Session-78 matrix) were selected in-sample too — a real finding (errata E56), not just my new sweep. The honest framing we landed on (headline = the binary verdict, prob_t operating points are an in-sample diagnostic reported as a sensitivity curve) came out of taking the conflict seriously rather than either of us being simply right.

Observation 39:
When CC framed the remaining 55-map 2×2 work as possibly needing a manual review, I steered toward "if it can all be managed via a crosstab script, great" — preferring the cheaper path explicitly — and it turned out the human-review CSVs already existed, so the crosstab script closed the gap (text-min + T=0.3) with no new 20-minute review. Naming the low-cost preference up front shaped the investigation toward checking what was already on disk before reaching for fresh effort.

Observation 40:
I asked CC to find which review we actually needed by reading back through the transcripts; it couldn't find it explicitly scoped, said so plainly instead of guessing, and we reasoned it out from the artifacts instead — the base 55maps-generalisation turned out to be the superseded original of text-high, so no review was needed. My imprecise memory ("complete a 2×2 / bring analyses into alignment") was enough to steer the search even though it didn't name the thing, and CC declining to confabulate a confident "yes, it's the one I queued" is what kept us off the wrong candidate set.

Observation 41:
Twice this session CC stopped itself from the convenient-but-wrong move without my prompting: it flagged that bumping GENERATOR_VERSION for new input data (not a logic change) would mislabel the provenance, and fixed the code comment to be honest about the bump being a batch milestone; and it reverted its own hand-edits to generated leaderboard files once it hit the anti-pattern (clobbered on regen, diverges from the cheap-render path), choosing the generator-only fix. Self-catching these rather than me having to flag them is exactly the discipline I want.

Observation 42:
On the N=1 baseline matrix (2026-06-02), CC offered three forks; I answered the easy one but asked to be *walked through* the other two — "could we discuss this? I want to make a careful, principled decision but I don't quite understand how buffers and MCC interact." Treating the methodology as something to understand before deciding, not merely approve, paid off twice: I caught that the matrix was below our 14-buffer standard (CC had been about to merge two stale 4-buffer files to work around it), and my "would MCC differ at 20 m vs 50 m?" edge case made CC re-read the scorer and *verify* MCC is buffer-free rather than assert it. Slowing the cadence to learn surfaced a real gap and forced a source-check.

Observation 43:
I set an explicit delegation boundary on the parallelisation work — "I trust your judgement on architectural decisions like spawn vs fork (I'm not such a proficient coder)" — while treating model versions as the thing to confirm (my CLAUDE.md marks them CRITICAL). Trust the engineering, ratify the science. That division let the session move fast where it was safe (CC chose spawn-over-fork and explained the multi-threaded-fork deadlock risk) and slow where it mattered (the `gemini-3.1-pro` model-of-record came to me for sign-off before being encoded, against a meta that said flash). The right split for a domain expert who isn't a programmer.

Observation 44:
I set the repo policy explicitly — commit direct to main, no PRs — on noticing CC default to the voluntary-PR / feature-branch pattern. Since the harness changes a couple of weeks ago, CC is primed *not* to commit autonomously and *not* straight to main: a sensible default for collaborative software development, but it brings real friction to a single-author research repo, where direct-to-main is the norm and a PR has no second reviewer to serve. Naming the single-author norm once (and CC capturing it to memory) removes the recurring friction.

Observation 45:
Three times this session (2026-06-03) CC posed a fork as a multiple-choice question — the tie-set method, the preregistration framing, how to record the Flash-not-Pro cells — and three times I declined the menu and asked to discuss instead. Each discussion produced a better frame than the options on offer: the prereg framing became a reusable template with a "justified ≠ confirmatory" distinction I drew in conversation; the model-identity fork became a triple-check-then-re-run path none of CC's three options contained. For a bounded choice (which buffer, which library) the menu is efficient, but for an open research-judgement call it closes the option space before I've shaped it. I'd rather reason *toward* the decision with CC than ratify its enumeration — on these forks the discussion is the work, and the multiple-choice skips it.

Observation 46:
Before authorising the genuine-Pro re-run I told CC "we can't afford to undertake this run more than once… be sure all configs are correct." The run itself was cheap (~$25) and trivially repeatable — what's *not* repeatable is a silently mis-parametered run that completes, scores plausibly, and contaminates a published comparison with an uncontrolled variable nobody catches. Naming the one-shot constraint pushed CC to audit the things that fail *invisibly* — recomputing the config library/instruction hashes against the March originals (byte-identical, not merely "the file exists"), and proving the batch↔realtime prompt assembly is equivalent — rather than just confirming the run would launch. The expensive failure mode here is invisible, not the dollar cost, and that's where the rigour should go.

Observation 47:
When CC was ready to plan the re-run, I stopped it: "before we decide on next steps, let's explicitly discuss the value of these passes versus the Pro passes we already have — what do they add?" Refusing to authorise spend until the marginal scientific value was articulated surfaced that the genuine Pro data we already hold sits on *one diagonal* of the thinking×temperature grid (so thinking and temperature are confounded and can't be separated), and that the untested HIGH/T=0.0 corner could lift the leaderboard ceiling. That's a real justification — completing a factorial we can actually analyse — not "finish the matrix for tidiness." I'd rather name the value explicitly before spending than discover after that the data didn't earn its cost.

Observation 48:
I caught CC asserting the preregistration's preliminary runs used Gemini 2.x — "Gemini 3 was released mid-November, and I'm pretty sure none of the runs are 2.x" — and it verified (zero `gemini-2.x` strings anywhere in configs/prereg/registry) and corrected its own unverified "earlier ⇒ older model" assumption. The same session turned up the deeper cost of exactly the habit that confabulation rhymes with: the `pro-*` slugs encode a model identity that turned out false (those cells were Flash), and I noted "we really must stop encoding info into filenames." The fix stayed documentation-not-renaming, per our E57 precedent — but the slug-as-truth trap keeps recurring, and it's worth a standing wariness of any fact a filename claims.

Observation 49:
When CC found two of the genuine-Pro cells were ~5% incomplete, it offered three ways to compose the n=3 *around* the bad pass — drop it, pay to replace it, or keep it with a caveat. I declined all three and said "clear all failures via recovery," our standing practice, which *fixes* the hole rather than working around it. CC's options all silently assumed the bad data was a constraint to live with; the repair option dominated all three and it hadn't framed it. This is Obs 45's menu-vs-discussion pattern again, but sharper: this time the option CC left off the menu was the correct one. Before "how do we cope with degraded data X?", the prior question is "can X simply be repaired?" — and my standing practices belong on the menu as first-class options, not afterthoughts.

Observation 50:
Reviewing the finding before sign-off, I asked CC to trim the cited outcome to report the result cleanly — "a little less of how the sausage is made, UNLESS you think it's material?" Its judgement was right and worth keeping: the recovery / coverage-hole detail is *not* material to the finding (→ trim to the audit trail), but the genuine-Pro-vs-Flash fact *is* material to validity (→ kept as a one-line pointer, since deviations:[E57] already carries it). What belongs in a cited finding versus its provenance is my call to set as the one who'll defend the paper, and CC's to implement. The "unless it's material?" check is the right shape — it delegates the judgement while inviting the push-back if I'm wrong.

Observation 51:
I flagged what looked like an inverted replicate allocation — we'd run the "deterministic" T=0.0 at n=3 but the stochastic T=0.7 at n=1 — and asked CC to /remember "don't run n>1 on T=0.0." CC checked the premise before recording it and found T=0.0 is NOT deterministic for this model (three replicates differed: 443/437/450 detections), so it declined to bake the memory and I agreed. My question was still productive — it triggered the determinism check and confirmed the n=3 was worthwhile — but the rule I proposed was false, and CC measuring rather than ratifying a confident-sounding premise is what kept a wrong heuristic out of memory. I'd rather have my plausible defaults checked than encoded.

Observation 52:
I delegated wide this session — "continue as far as you can [through Batches B/D/E], ask for help when needed, I'll leave those decisions to you" — a deliberate step up from the per-fork AskUserQuestion cadence of recent sessions (cf. Obs 45/49). What made it work was CC *triaging* the asks rather than either asking on every grain choice or proceeding on all of them: it surfaced exactly two forks (the proposer-verifier-384 condition grain; how to handle the phase2/phase3 Era-1 runs) and authored the precedented rest itself. Both asks turned out to sit on genuine forks — one revealed that "re-score phase2" wasn't the simple operation we'd both assumed (its metric is a replicate-mean over K passes with no MCC, so it's a bespoke script-rework, not a Batch-C-style rescore), and the other let CC defer rather than mis-attribute a whole Era-2 corpus (pv-diag-384's consensus sweeps) to an Era-1 run (retest-phase3a) — the "phase3a" name collision. Wide delegation only pays off if the delegate knows which decisions are still mine; this session it did. The menu-vs-discussion tension (Obs 45/49) doesn't vanish under delegation — it becomes a triage problem: spend my attention only on the non-defaultable, hard-to-reverse forks.

Observation 53:
Two sessions ago (Obs 48) I caught CC asserting the preliminary runs used Gemini 2.x; this session we finished the job — it's a repo-wide confabulation, and the model-of-record is `gemini-3-flash`. The part worth keeping: after CC had resolved the metas-vs-prose conflict the dull way ("someone mistyped a model name"), I offered my actual recollection — the early Antigravity work ran on Gemini 3, which had a bug of insisting it was Gemini 2.x, and that contaminated the repo. CC didn't just adopt my story because it was convenient; it tested it against the raw Antigravity logs and found my memory was right almost verbatim. My fallible recollection turned out to be a sharper pointer to the truth than the project's own authored result docs — but only because CC treated it as a hypothesis to verify, not a fact to accept.

Observation 54:
On the consensus-conditions granularity fork — 29 headline conditions vs all 249 sweep points — I declined CC's multiple-choice and said I'd rather talk it through. I leaned toward "individual citable conditions despite the high count" but wasn't sure, and asked for whatever was most consistent with what we'd done and most legible going forward. That pushed CC to ground the decision in evidence rather than either of our preferences: it re-read how Batch C (the one sweep we'd already decomposed) actually handled it — one operating point per cell at vote≥4, the rest left unclaimed — and recommended the same shape here (one citable condition per config at best-F1@20m, plus the full sweep as a 3c analysis), which honoured my "individual citable" instinct at the *config* level without ballooning to 249 rows. I then had it `/remember` the pattern as a model for the future phase3a/3c work. Two things worth keeping: declining the poll to converse turned a one-off grain choice into a reusable convention; and anchoring the choice in precedent — not in what either of us *felt* was right — is what made it defensible. The right output of a granularity fork is sometimes a standing rule, not just an answer. (Contrast Obs 52, where my "re-score phase2 is bespoke" framing rode into this session and CC found it wasn't — inherited *framing* needs the same precedent-check that a fresh fork gets.)

Observation 55:
I declined CC's first sign-off on the diversity-dividend finding and said "I'd like to briefly discuss how we frame things" — and that one move did two things that turned out to be facets of the same correction. First, it caught a *category error* CC had reflexively committed: it had wrapped a clean result in an "in-sample / not-deployable" caveat (a statistician's winner's-curse caution), and my sense that we were over-complicating and hedging was right — selecting the best (N, threshold) against the GS test tiles IS the preregistered H3 method (`analysis-summary.md` §H3), because those tiles are the measurement instrument, not a proxy for unseen data. CC had imported the caution without checking whether the study's design made it apply. Second, the same conversation didn't just fix one finding — it let me articulate the whole boundary the finding sits on: the 4 GS maps are calibration+test that *establish* parameters; the 55-map run is production, reported against my manually-corrected student GT, with the curtain-pulled oracle-best and the carry-forward−best delta. That reframed the next analysis and the meaning of E56 too. The thing worth keeping: a domain expert's "this feels over-complicated, let's talk" is often both a precondition-check the statistical default skipped *and* a generative act — declining sign-off to discuss framing caught the category error AND surfaced a project-wide architecture that three sessions of decomposition had left implicit. The numbers were right by mid-session; the discussion is what made them *mean* the right thing. (CC's tell, which it logged itself: reaching for a domain default — "operating point selected on the eval set is optimistic" — without checking the domain's *precondition*, namely whether the eval set is the deliverable or a stand-in for the unseen.)

Observation 56:
When CC offered an `AskUserQuestion` on the test design, I took the *clarify* path and redirected it to do homework first — "explore the preregistered consensus threshold, if any" and "match other results reporting we have done." That forcing function produced a far better-grounded design than any menu option would have: it sent CC to `analysis-summary.md` §H3 (which settled the framing — best (N, threshold) against the test tiles is the preregistered output) and to how phase3a and the 55-map runs already reported operating points (which settled the granularity). This extends Obs 54: there, declining the poll to *converse* turned a grain choice into a convention; here, declining it to *direct the investigation* converted a design choice into an evidence question — and the evidence, not either of our preferences, set the answer. The pattern across both: my most useful move on a fork is often not picking an option but naming the homework that would make the option obvious.

Observation 57:
Across this session CC kept reaching for a plausible-enough default — a causal mechanism for *why* the looser 3-of-5 wins on deployment, a "good enough" cross-run ground truth built by just unioning my reviews — and I kept catching the subtlety it had skipped. The pattern worth naming: CC's failure mode is *confident sufficiency* (a mechanism that sounds right, a GT that's nearly right); mine, as the one who has to defend the paper, is *suspicion of my own conveniences*. On review-bound work the data-owner's scepticism has to override the assistant's first plausible explanation, and CC treating its own first answer as a hypothesis to attack rather than a conclusion to defend is exactly the disposition I want from it.

Observation 58:
I asked CC a single question about the "fixed-union" ground truth it had built — what did it do where I'd labelled the same tile differently from one review run to the next? — and that one question exposed *two* distinct problems it had missed: it was silently letting a 'mound' label override a 'not_mound', and the scorer never deduplicated, so a mound several runs found became several phantom points and spurious false negatives. Asking the right probing question surfaced more than reviewing its output would have. A reminder that my most useful move on a fork is often not picking an option but naming the question that makes the flaw visible.

Observation 59:
When CC explained why the looser 3-of-5 wins in deployment, it offered two mechanisms — the 50 m tolerance being "more forgiving" than the GS 20 m, and the corrected GT "crediting" the extra mounds. I pushed back: the 50 m is matched to the ~25 m student-digitisation jitter, not leniency, and "the metric rewards finding mounds" is just recall restated. CC dropped the mechanistic story for the honest one — the 4-map test set simply lacks the resolving power to separate neighbouring configs. The lesson I want to keep: anti-confabulation isn't only about invented identifiers; it applies to plausible-but-unfounded *causal* claims too. An honest "we can't tell from this set" beats a tidy mechanism the data doesn't support.

Observation 60:
Across a long, mostly-autonomous build this session, Shawn intervened almost entirely at the level of *what the paper needs* — the two-reference (historical / canonical) decomposition that organised the whole session, and "the argument is 4-of-5 vs 3-of-5, so we need both thresholds" (which expanded my tidy 5-cell plan to the 7 cells that actually carry the claim). He left the pipeline-correctness to me: the eCryptfs phantom diffs, a remote untracked-blocks-pull, a schema rejecting `@`, a drift-check failing on a missing field — all caught and self-fixed. The split worked *because* every step had a cheap objective gate (reproduce the prior F1 to 7 d.p.; diff the manifest "+7/0-changed" ts-normalised; drift-check hard fail-count) that let me self-correct without his auditing each move. A healthier division of labour than the previous session's turn-by-turn default-catching — and one that only holds when the verification gates are real.

Observation 61:
I proposed *deferring* the manifest registration to next session — "it's intricate, better mapped carefully than rushed at the tail of a long session." Shawn overrode it: "we have plenty of context, let's complete it." He was right that it was doable, and finishing it surfaced two genuine breakages (the schema forbids `@` in a condition_id; the drift-check failed four runs because my adapted eval omitted the `input_files` block) — which the gates caught immediately. The lesson I want to keep: "intricate" is a reason to *install verification gates and proceed*, not to defer. Deferral dressed up as prudence is just postponed risk handed to a future session that will face the same gates with less context. The honest move when something is delicate is to make its failure modes cheap to detect *now*.
