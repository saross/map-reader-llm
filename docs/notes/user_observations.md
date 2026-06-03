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
