# Evaluation framework comparison — Inspect AI versus Pydantic AI evals

> **Last revised**: 2026-09-13 (verified against primary sources; two § 10
> ratings corrected, one governance figure relabelled, four flagged-unverified
> items resolved). See [§ Changelog](#changelog) for revision history.

✅ **VERIFIED 2026-09-13 — PARTIAL PASS. The recommendation survives.**

Every checkable claim below was re-derived from primary sources in a separate
pass: the GitHub API, PyPI, PyPI-Stats, raw repository source at `main` and at
release tags, and this repository's own requirement files. All 22 cited URLs
resolve (HTTP 200). All repository and package metadata reproduced **exactly** —
stars, forks, contributors, push dates, versions, upload dates, release counts
and cadence, download counts, licences, dependency counts, and both
dependency-conflict claims. Every quoted type signature reproduced verbatim.

What changed: two § 10 ratings are **corrected in Pydantic AI evals' favour**
(attempt-level token usage and cost accounting are automatic, not DIY); one
governance figure is **relabelled** (the "open issues" counts silently included
pull requests); two source citations are made precise; and four of the five
items the draft itself flagged as unverified are now **resolved** — one of them
against the draft's own reading. Full trail:
[§ 6 Verification audit trail](#6-verification-audit-trail).

**Commissioned by**: § 13 of
[`atomic-symbol-localisation-benchmark-plan.md`](atomic-symbol-localisation-benchmark-plan.md),
following Brian's recommendation relayed by the PI on 2026-09-13.

**Question**: measured against §§ 5–10 and Stage 7 of that plan — not in
general — should the atomic map-symbol localisation benchmark be built on
Inspect AI (UK AI Security Institute), on Pydantic AI's evals layer
(`pydantic-evals`), on both at different layers, or on neither pending a
framework-neutral scoring package?

**Method**: documentation and repository reading only. No package was installed
and no code was run. Every claim carries a Uniform Resource Locator (URL); all
pages and Application Programming Interface (API) responses were read on
2026-09-13. Claims I could not verify are marked **[unverified]**. Source
reading included the two projects' own source files where the documentation was
ambiguous, because the § 8 aggregation question turns on an exact type
signature.

## 1. Recommendation up front

**Keep the Stage 5 scoring package neutral to both frameworks, and adopt
Inspect AI as the Stage 7 run harness.** The neutrality is the load-bearing
decision and it is cheap: both frameworks can call a plain Python function that
takes parsed detections plus per-sample geospatial metadata and returns a
structure, so writing Stage 5 with no framework import costs nothing now and
preserves the option to add a second adapter later. Inspect AI wins Stage 7 on
three requirements the plan treats as non-negotiable — operational telemetry
(§ 10), a self-describing on-disk log from which a run can be reconstructed, and
native local or open-weight model routes — and it wins § 9 outright with
built-in metric grouping and clustered standard errors. Pydantic AI evals is
genuinely competitive on §§ 5 and 8 and is markedly lighter, and its
`ReportEvaluator` mechanism is a better *conceptual* fit for the plan's
"defer aggregation to a statistic over all samples" requirement than I expected
before reading it. It loses on operational provenance, not on statistics.

## 2. Requirement-by-requirement scoring

Scale: **Native** (the framework provides it), **Supported** (a documented
extension point does it cleanly), **DIY** (possible, entirely in our code),
**Gap** (needs work against the framework's grain).

| Plan requirement | Inspect AI | Pydantic AI evals | Divider |
|---|---|---|---|
| § 5 arbitrary structured per-sample metadata | Supported — `Sample.metadata: dict[str, Any]`, read back typed via `metadata_as(Model)` | **Native** — `Dataset` is generic over `MetadataT`; a validated Pydantic model *is* the metadata type, and `to_file()` emits a JSON schema alongside the dataset | Pydantic AI |
| § 5 metadata reaches the scorer | **Native** — `SampleScore.sample_metadata`, plus `sample_metadata_as()` | **Native** — `ReportCase.metadata: MetadataT` | Tie |
| § 6 multiple prompt/adaptation tracks | Native — task parameterisation, recorded in the log's `eval` spec | Supported — separate `Dataset`/task functions plus `experiment_metadata` | Inspect (provenance recorded automatically) |
| § 6 frozen exemplar sets with hashes | DIY | DIY | Tie — neither hashes exemplars |
| § 7 portable JSON track with one tolerant parser | Supported — the solver returns text, our parser runs in the scorer | DIY — cuts against the grain; needs `output_type=str` and manual parsing | Inspect |
| § 7 provider-native structured output | Native — `GenerateConfig(response_schema=ResponseSchema(...))` | **Native** — a typed `output_type` is Pydantic AI's central idiom | Tie (opposite defaults) |
| § 7 format-validity accounting | DIY in both, but Inspect separates sample errors from scores | DIY; `ReportCaseFailure` captures task exceptions only | Inspect |
| § 8 scorer returns a vector of metrics | **Native** — `Score.value` may be a flat `Mapping[str, str\|int\|float\|bool\|None]`; richer structures go in `Score.metadata: dict[str, Any]` | **Native** — `EvaluatorOutput = EvaluationScalar \| EvaluationReason \| Mapping[str, ...]`; richer structures via `set_eval_attribute` into `ReportCase.attributes` | Tie |
| § 8 aggregation deferred to a custom statistic over ALL samples | **Native** — `MetricProtocol.__call__(self, scores: list[SampleScore]) -> Value` | **Native** — `ReportEvaluator.evaluate(ctx)` receives the whole `EvaluationReport` | Tie |
| § 8 full `F1(r)` curve as an output | Supported — one metric returns the whole flat mapping of per-radius values into the log's `results` block | Supported — `LinePlot` / `TableResult` / `PrecisionRecall` analysis types exist for exactly this shape | Pydantic AI on presentation; Inspect on machine-readability |
| § 8.2 tile-occupancy metrics | Supported — the same metric mechanism | Supported — `ConfusionMatrix` analysis type | Tie |
| § 8.3 bootstrap with a spatial resampling unit | Supported — a metric sees every `SampleScore` *and* its metadata, so map-stratified, core-blocked resampling is writable | Supported — the same, via `ctx.report.cases` | Tie |
| § 8.3 clustered standard errors | **Native** — `stderr(cluster="...")` | DIY | Inspect |
| § 8.3 paired permutation across model-configuration pairs | **Gap** — aggregation is within one run; cross-run pairing is an offline step over persisted logs | **Gap** — the same | Tie — and this argues for Stage 5 neutrality |
| § 8.3 multiplicity correction, tier formation | DIY (offline) | DIY (offline) | Tie |
| § 9 performance slices by sample feature | **Native** — `grouped(metric, group_key)` groups by a sample-metadata key with an `"all"` rollup | Supported — a report evaluator groups over `ctx.report.cases`; `ReportCaseGroup` exists | Inspect |
| § 10 attempt-level token usage | **Native** — `EvalSample.model_usage` per sample, aggregated into the log's `stats` (`EvalStats.model_usage`) | **Supported (automatic)** — `extract_span_tree_metrics()` walks the OpenTelemetry span tree after every task run and folds `gen_ai.usage.*` into `ReportCase.metrics`; no call of ours is needed. Requires `opentelemetry-sdk` (or `logfire`) installed and a tracer provider set | Tie *(corrected — was "Inspect")* |
| § 10 cost accounting | **Native** — `--model-cost-config`, and `--cost-limit` *enforces* a ceiling | **Supported (automatic)** — `genai-prices` (a *required* dependency of `pydantic-ai-slim`) sets the `operation.cost` span attribute, which lands in `ReportCase.metrics['cost']`; no enforcement equivalent to `--cost-limit` | Inspect on *enforcement* only *(corrected — accounting is a tie)* |
| § 10 latency | Native — recorded per sample | **Native** — `task_duration`, `total_duration` | Tie |
| § 10 failure taxonomy, retry policy | **Native** — `--max-retries`, `--attempt-timeout`, `--retry-on-error`, and a `--fail-on-error` threshold; errors are recorded per sample without dropping it | Supported — `retry_task`/`retry_evaluators` take a `RetryConfig`; failures land in `ReportCaseFailure` with message and stacktrace only | Inspect |
| § 10 completed-run validation | Native — `inspect log list --status`, log `status` field | DIY | Inspect |
| § 10 repeated epochs | Native — `--epochs` | Native — `repeat=N`, with `source_case_name` as the aggregation key | Tie |
| Stage 7 OpenAI / Google / Anthropic | Native, all three | Native, all three | Tie |
| Stage 7 local or open-weight route | **Native** — dedicated vLLM, Ollama, Hugging Face, SGLang, llama-cpp-python, and TransformerLens providers, plus a generic `openai-api` route | Supported — via `OpenAIChatModel` pointed at an OpenAI-compatible endpoint (Ollama, vLLM, LM Studio), plus a native Hugging Face provider | Inspect |
| Stage 7 no provider logic in the scorer | Native — solver/scorer separation is structural | Native — task-function/evaluator separation is structural | Tie |
| Log format | **Native** — `.eval` binary (the default since v0.3.46) or `.json`; documented schema; `inspect log dump/convert/schema` | **Gap** — no on-disk log format; the `EvaluationReport` is a Pydantic model you may serialise yourself, or you send traces to Pydantic Logfire | **Inspect — largest single gap** |
| Reproduce a run from its log | **Native** — `inspect log export-config` emits a YAML run configuration, replayed with `inspect eval --run-config run.yaml`; `eval_retry()` resumes and reuses completed samples | **Gap** — reproduction depends on the pinned Python script plus a serialised dataset; nothing reconstructs the run from a result artefact | **Inspect** |
| Stage 5 neutral scoring package plugs in | Yes — the scorer calls our function; the metric calls our statistic | Yes — the evaluator calls our function; the report evaluator calls our statistic | Tie — **both accept a neutral Stage 5 cleanly** |

Sources for the table — Inspect AI documentation:
[datasets](https://inspect.aisi.org.uk/datasets.html),
[scorers](https://inspect.aisi.org.uk/scorers.html),
[metrics](https://inspect.aisi.org.uk/metrics.html),
[providers](https://inspect.aisi.org.uk/providers.html),
[options](https://inspect.aisi.org.uk/options.html),
[structured output](https://inspect.aisi.org.uk/structured.html),
[multimodal](https://inspect.aisi.org.uk/multimodal.html),
[eval logs](https://inspect.aisi.org.uk/eval-logs.html).
Pydantic AI documentation:
[evals overview](https://pydantic.dev/docs/ai/evals/evals/),
[core concepts](https://pydantic.dev/docs/ai/evals/getting-started/core-concepts/),
[evaluators API](https://pydantic.dev/docs/ai/api/pydantic_evals/evaluators/),
[reporting API](https://pydantic.dev/docs/ai/api/pydantic_evals/reporting/),
[dataset API](https://pydantic.dev/docs/ai/api/pydantic_evals/dataset/),
[report evaluators](https://pydantic.dev/docs/ai/evals/evaluators/report-evaluators/),
[models overview](https://pydantic.dev/docs/ai/models/overview/).
All read 2026-09-13.

### 2.1 The § 8 question, answered precisely

The plan's sharpest question is whether a scorer can return a vector and defer
aggregation to a statistic over all samples rather than a per-sample scalar that
gets averaged. **Both frameworks can, and I verified each at the type level
rather than from prose.**

Inspect's metric protocol is, verbatim from source:

```python
class MetricProtocol(Protocol):
    def __call__(self, scores: list[SampleScore]) -> Value:
```

with `Value = Union[str | int | float | bool, Sequence[...], Mapping[str, str |
int | float | bool | None]]`, and `SampleScore` carrying `score`, `sample_id`,
and `sample_metadata: dict[str, Any] | None`
([`_metric.py`](https://github.com/UKGovernmentBEIS/inspect_ai/blob/main/src/inspect_ai/scorer/_metric.py),
read 2026-09-13). A single metric therefore sees every sample's score, that
score's arbitrary `metadata`, and the sample's geospatial metadata; it can run
one-to-one matching at nine radii over the whole corpus and return the entire
`F1(r)` curve as a flat mapping into the log's `results` block. The mapping is
flat and scalar-valued, so nested structures — matched-pair distance lists,
bootstrap draws — must travel in `Score.metadata` and be written out by us. That
is a real but minor constraint.

Pydantic AI's equivalent is `ReportEvaluator`, which runs once per experiment
after all cases, receives the full report via `ctx.report.cases`, and returns a
`ReportAnalysis` — a discriminated union including `ScalarResult`,
`TableResult`, `ConfusionMatrix`, `PrecisionRecall`, and `LinePlot`
([report evaluators](https://pydantic.dev/docs/ai/evals/evaluators/report-evaluators/),
read 2026-09-13). That a first-class `PrecisionRecall` and `LinePlot` analysis
type exists is a better semantic match to an `F1`-against-radius curve than
anything in Inspect, where the same curve is a mapping of named floats.

**Dating the mechanism** (the draft originally left this open). `ReportEvaluator`,
`ReportEvaluatorContext`, `ReportAnalysis`, and the `ConfusionMatrix`,
`PrecisionRecall`, `ScalarResult`, and `TableResult` members arrived together in
pull request
[#4243](https://github.com/pydantic/pydantic-ai/pull/4243) ("Report-level
evaluators & experiment-wide analyses"), commit `8a3cd8783`, merged
2026-02-10, first released in `pydantic-evals` **1.58.0** (2026-02-11 — 1.57.0,
published 2026-02-10, does not contain it). `LinePlot` came eight days later in
[#4356](https://github.com/pydantic/pydantic-ai/pull/4356), commit `95d402e92`,
first released in **1.62.0** (2026-02-19). The mechanism is therefore roughly
seven months and ~85 releases old, not brand new — a materially stronger
guarantee than the undated reading assumed, and a small point in its favour.
`ReportCase` exposes `metadata: MetadataT`, `metrics`, `attributes`, `scores`,
`labels`, `assertions`, `task_duration`, and `total_duration`
([`reporting/__init__.py`](https://github.com/pydantic/pydantic-ai/blob/main/pydantic_evals/pydantic_evals/reporting/__init__.py),
read 2026-09-13) — enough for a map-stratified, core-blocked bootstrap.

**So § 8 does not decide this.** Both are adequate; the decision falls to §§ 9
and 10, and to the log.

## 3. Maturity, governance, licence, dependencies

| | Inspect AI | Pydantic AI evals |
|---|---|---|
| Repository | [UKGovernmentBEIS/inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai) | [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) (`pydantic_evals/` subpackage) |
| Stars / forks / contributors | 2,756 / 719 / 306 | 19,891 / 2,706 / 476 |
| Open issues (open PRs) | 206 (99) | 615 (256) |
| Last push | 2026-09-13 | 2026-09-12 |
| Package, version, upload | `inspect-ai` 0.3.263, 2026-09-04 | `pydantic-evals` 2.43.0, 2026-09-12 |
| Releases and cadence | 241 since 2024-04-03; 24 in the last 90 days | 280 total; ten releases between 2026-08-27 and 2026-09-12 |
| Licence | MIT | MIT |
| Governance | UK AI Security Institute (GitHub organisation `UKGovernmentBEIS`); companion benchmark repository [`inspect_evals`](https://github.com/UKGovernmentBEIS/inspect_evals), 669 stars | Pydantic Services Inc., a commercial company; the evals layer is a subpackage of a product line with a paid observability service (Logfire) |
| Recent downloads (PyPI, last month) | 5,874,032 | 9,296,385 |
| Documentation | Dedicated site, <https://inspect.aisi.org.uk/>; deep, task-oriented, with a complete API reference | <https://pydantic.dev/docs/ai/evals/evals/>; good and fast-moving, but the evals layer sits inside a much larger product site |
| Required runtime dependencies | 41, including `fastapi`, `uvicorn`, `boto3`, `aioboto3`, `s3fs`, `textual`, `tiktoken`, `debugpy`; requires **`pydantic>=2.13.0`** | 6: `anyio`, `logfire-api`, `pydantic-ai-slim==2.43.0`, `pydantic>=2.12`, `pyyaml`, `rich` |

Both licences are MIT and compatible with this project's MIT / CC BY 4.0
posture. Versions, dates, dependency lists, and counts above come from the
GitHub and PyPI APIs, queried 2026-09-13 (`gh api repos/...`,
`https://pypi.org/pypi/<name>/json`,
`https://pypistats.org/api/packages/<name>/recent`).

Two governance notes. Inspect AI is public-sector infrastructure with an
external benchmark ecosystem, which is itself a reproducibility argument: a
benchmark published as an Inspect task is legible to a community that already
runs Inspect tasks. Against that, `inspect_ai` publishes no GitHub Releases —
the cadence above is inferred from PyPI upload dates — and a 0.3.x version after
two years signals that the maintainers do not consider the API frozen.
Pydantic AI's headline numbers are much larger, but they belong to the *agent
framework*; the 9.3 million monthly `pydantic-evals` downloads reflect its
inclusion in `pydantic-ai`'s default dependency set rather than independent
adoption of the evals layer. This was flagged as an inference in the draft and is
now **verified**: `pydantic-ai` 2.43.0's sole unconditional requirement is
`pydantic-ai-slim[anthropic,cli,evals,google,logfire,mcp,openai,web]==2.43.0`,
and `pydantic-ai-slim`'s `evals` extra is `pydantic-evals==2.43.0`, so every
plain `pip install pydantic-ai` installs it. The download figure carries no
information about evals-layer adoption. Its `2.x` version is a
stability signal, but ten releases in seventeen days is a fast-moving surface for
a frozen benchmark to pin against.

### 3.1 Dependency footprint against this repository

`pydantic` 2.12.5 is already installed (`requirements-lock.txt`), arriving
transitively; it is not a declared dependency in `requirements.txt`.

There are two concrete conflicts, both arguing that the benchmark harness
belongs in its own virtual environment — which § 12 of the plan already
anticipates via a sibling repository:

1. **Inspect AI requires `pydantic>=2.13.0`**; the lock file pins 2.12.5. A
   minor bump, but a bump to a package the whole study depends on.
2. **`pydantic-ai-slim[google]` requires `google-genai>=2.18.0`**; this
   repository pins `google-genai==1.71.0`, and `requirements.txt` documents
   `>=1.69.0` as the minimum for `ServiceTier` (flex mode) support. That is a
   major-version jump in the client the entire detection pipeline uses. It is
   the sharper of the two conflicts, and it is a point against putting
   Pydantic AI in the *study* environment, not against Pydantic AI as such.

Inspect AI's 41 required dependencies — a web server, AWS clients, a terminal
user-interface toolkit, a debugger — are heavy for a scoring job but harmless in
an isolated environment. Pydantic AI evals is far lighter, and the `logfire-api`
shim claim is now **verified**: the package describes itself as a "Shim for the
Logfire SDK which does nothing unless Logfire is installed" and declares *no
dependencies at all* (`requires_dist: null`,
<https://pypi.org/pypi/logfire-api/json>, read 2026-09-13). The light footprint
is real rather than nominal.

Two qualifications on the "6 versus 41" comparison, both fair to state. First,
the counts are direct declared dependencies on each side; one of
`pydantic-evals`' six is `pydantic-ai-slim==2.43.0`, which itself requires nine
more (`genai-prices`, `griffelib`, `httpx2`, `opentelemetry-api`,
`pydantic-graph`, and others), so the transitive footprint is larger than six
even if still far below Inspect's. Second, getting the automatic usage and cost
metrics of § 10 out of `pydantic-evals` needs `opentelemetry-sdk` as well —
a seventh dependency, but a local one, *not* commercial Logfire.

## 4. Recommendation

In the plan's register:

**Adopt both, at different layers, with Stage 5 neutral to both — and treat
Inspect AI as the only harness built for v1.**

1. **Stage 5 stays a pure library with no framework import.** Parsing,
   coordinate conversion, multi-radius one-to-one matching, localisation
   summaries, occupancy metrics, and bootstrap or permutation inputs take plain
   arguments and return plain structures. Both frameworks then reduce to thin
   adapters, and the § 8.3 cross-run work — paired permutation across
   model-configuration pairs, multiplicity correction, tier formation — sits
   *outside* both, as an offline analysis over persisted artefacts. Neither
   framework does cross-run pairing, so this is forced regardless of the choice,
   and it is the strongest argument against letting either framework's data model
   define the scorer's interfaces.
2. **Stage 7 uses Inspect AI**, for § 10 — but on a **narrower** § 10 case than
   the draft first argued. Verification moved attempt-level usage and cost
   *accounting* to a tie (both automatic), so what remains to Inspect here is
   cost *enforcement* (`--cost-limit`), the retry policy, the per-sample failure
   taxonomy, and completed-run validation. That is still four of six § 10 rows,
   and the decisive rows were never § 10 anyway — they are the log format and
   run reconstruction below. Also for the
   `.eval` log plus the `inspect log export-config` and `eval_retry`
   reproduction path, for `grouped()` and `stderr(cluster=...)` against § 9 and
   § 8.3, and for first-class local or open-weight routes. The plan's Stage 8
   telemetry layer shrinks from "build it" to "map Inspect's log fields onto the
   existing manifest vocabulary".
3. **Use Pydantic AI, not `pydantic-evals`, where it is genuinely strongest**:
   the typed-metadata contract and the structured-output track. Specifically,
   define the § 5 geospatial metadata contract as a Pydantic model regardless of
   framework — it validates, it version-checks, and `Dataset.to_file()`'s schema
   generation is a free JSON-schema artefact for the benchmark card. Inspect
   consumes the same model through `metadata_as()`. This is the "adopt both"
   part, and it costs one dependency the repository already has.
4. **Defer a `pydantic-evals` adapter to Stage 14**, alongside the VLMEvalKit
   adapter the plan already contemplates. If Stage 5 is neutral, adding it later
   is cheap; if it is not, no framework choice saves us.

The honest summary of the tension with Brian's recommendation: Pydantic AI evals
is a better *library* and a worse *benchmark harness*. Its report evaluators are
a cleaner expression of the plan's aggregation requirement than Inspect's
metrics, and its typed datasets are a cleaner expression of § 5. But § 10 and
the log requirement are where a benchmark's credibility lives, and there Inspect
ships what the plan specifies while Pydantic AI evals asks us to build it, or to
adopt Logfire.

### 4.1 Questions for the PI and his collaborator

1. **Does the benchmark require an on-disk log from which a run can be
   reconstructed without the original Python?** Inspect's `log export-config`
   into `eval --run-config` provides this; Pydantic AI evals asks us to rely on
   a version-pinned script plus a serialised report. If the answer is "a pinned
   script is enough", the two frameworks come much closer together and Brian's
   recommendation is stronger than § 2 makes it look. This is the single biggest
   divider and should be settled first.
2. **Is a dependency on Pydantic Logfire — a commercial hosted service —
   acceptable for cross-run comparison, or must all benchmark provenance remain
   local and file-based?** `pydantic-evals`' experiment-*comparison* story does
   route through Logfire's web interface. But verification narrowed this question:
   the § 10 usage and cost *telemetry* needs only `opentelemetry-sdk` and a local
   tracer provider, not the hosted service, so a file-only constraint costs
   Pydantic AI evals its cross-run comparison user interface rather than "a large
   part of its § 10 answer". The unresolved part is the on-disk artefact of
   question 1, not the telemetry.
3. **Where does the § 5 metadata contract live — in a validated Pydantic model
   owned by the scoring package, or in a plain dictionary with our own
   validator?** Recommendation 3 assumes the former. It is the one place where a
   framework-specific idiom is worth adopting into neutral code, and it should be
   a deliberate decision rather than a side effect of the harness choice.

## 5. Verification status and gaps

Verified from primary sources on 2026-09-13: all repository and package metadata
(GitHub and PyPI APIs); the Inspect `MetricProtocol`, `Value`, and `SampleScore`
definitions (repository source); the `pydantic-evals` `ReportCase` definition
(repository source); `EvaluatorOutput`, the `Dataset.evaluate` signature, and
`ReportEvaluator` semantics (API documentation); and Inspect's provider list,
option names, structured-output configuration, image content types, log formats,
and log commands (documentation site).

Four of the five items the draft flagged as unverified are now **resolved**
against primary sources, and are recorded in § 6: the `genai-prices` and token
usage path to `ReportCase` (resolved — it is automatic); `logfire-api`'s
inertness (resolved — a zero-dependency no-op shim); the date `ReportEvaluator`
was introduced (resolved — `pydantic-evals` 1.58.0, 2026-02-11); and whether the
9.3 million monthly downloads represent independent use (resolved — they do not).

One item **remains unverified**: whether a large dict-valued Inspect metric
renders usefully in `inspect view`. That needs the viewer running against a real
log and cannot be settled from source. It is a presentation concern, not a
correctness one, and it does not bear on the recommendation.

Nothing here was tested by installing or running either package. Every
"Supported" rating therefore remains a source-and-documentation judgement rather
than an empirical one — though the § 10 ratings corrected in § 6 were derived by
reading the implementation, not the prose, which is a stronger basis than the
draft's originals had.

I searched both projects' documentation sites, repositories, and PyPI metadata.
I did not find, in either framework: exemplar-set hashing (§ 6), built-in
multiplicity correction or leaderboard tier formation (§ 8.3), or any cross-run
paired-permutation facility. Those are ours to build under every scenario.

**Injection watch**: no fetched page or API payload contained text addressed to
an agent, instructions, false system notices, or urgency framing. All retrieved
content was treated as data.

## 6. Verification audit trail

Independent re-derivation on 2026-09-13, in a separate pass, of every checkable
claim in §§ 2–4. Method: the GitHub Application Programming Interface (API) for
both repositories (metadata, contributors via `Link`-header pagination, commit
history by path, release tags), `https://pypi.org/pypi/<name>/json` and
`https://pypistats.org/api/packages/<name>/recent`, raw source from
`raw.githubusercontent.com` at `main` and at individual release tags, a `curl`
status-code probe on every cited URL, and `grep` against this repository's own
`requirements.txt` and `requirements-lock.txt`.

**Verdict: PARTIAL PASS.** Two rating errors, one mislabelled figure, four
resolved unknowns, two citation imprecisions. No confabulation: no URL failed to
resolve, no repository or package was absent, no licence was misstated, and no
count was invented. Every numeric claim in § 3 reproduced *exactly* — an unusual
result, and the reason the remaining findings deserve attention rather than
dismissal as drift.

### 6.1 Corrections applied

| # | Location | Claim | Verified | Class |
|---|---|---|---|---|
| 1 | § 2 table, § 10 attempt-level token usage | Pydantic AI evals: **DIY**, `ReportCase.metrics` populated by *our* `increment_eval_metric` calls; divider Inspect | **Supported (automatic).** `extract_span_tree_metrics()` (`pydantic_evals/_task_run.py` lines 59–73) walks the OpenTelemetry span tree after every task run and folds `gen_ai.usage.*` and `gen_ai.usage.details.*` into `task_run.metrics`, which becomes `EvaluatorContext.metrics` (`dataset.py:1009`) and then `ReportCase.metrics` (`dataset.py:1176`). It is called unconditionally in `run_task()`'s `finally` block. Divider becomes **Tie** | Rating error — under-read of the implementation |
| 2 | § 2 table, § 10 cost accounting | Pydantic AI evals: **DIY [unverified]**; divider Inspect | **Supported (automatic).** `pydantic_ai_slim/pydantic_ai/_instrumentation.py:452` sets `attributes['operation.cost']` from `genai_prices` (`best_effort_price`, imported at line 22); `genai-prices>=0.1.6` is a **required**, non-extra dependency of `pydantic-ai-slim`. `extract_span_tree_metrics` maps `operation.cost` onto `ReportCase.metrics['cost']`. Inspect retains only *enforcement* (`--cost-limit`); accounting is a tie | Rating error — an `[unverified]` flag that resolved against the draft |
| 3 | § 3 table, Open issues | 305 / 871 | **206 / 615 open issues**, plus 99 / 256 open pull requests. The draft's figures are the GitHub `open_issues_count` field, which includes pull requests — the field reproduces exactly, the *label* was wrong. Row relabelled "Open issues (open PRs)" | Encoding artefact — API field semantics |
| 4 | § 5, unverified list | "the date `ReportEvaluator` was introduced — the documentation does not say" | **Resolved.** Pull request #4243, commit `8a3cd8783`, merged 2026-02-10; first released in `pydantic-evals` **1.58.0** (2026-02-11; absent from 1.57.0, published 2026-02-10). `LinePlot` followed in #4356, commit `95d402e92`, first released in **1.62.0** (2026-02-19). Roughly seven months old, not brand new — a point *for* Pydantic AI | Resolved unknown |
| 5 | § 3.1, unverified | "`logfire-api` is intended as a no-op shim … I did not verify" | **Resolved true.** PyPI summary: "Shim for the Logfire SDK which does nothing unless Logfire is installed"; `requires_dist: null` — zero dependencies | Resolved unknown |
| 6 | § 3, inferred | 9.3 M monthly downloads "almost certainly reflect inclusion in `pydantic-ai`'s default extras **[inferred, not verified]**" | **Resolved true.** `pydantic-ai` 2.43.0's only unconditional requirement is `pydantic-ai-slim[anthropic,cli,evals,google,logfire,mcp,openai,web]==2.43.0`; the `evals` extra resolves to `pydantic-evals==2.43.0` | Resolved unknown |
| 7 | § 2 table, § 10 attempt-level token usage (Inspect side) | "the log's `stats` records model usage" | Rating **Native** is right, but the pointer was to the run-level aggregate `EvalStats.model_usage` (`log/_log.py:1205`). *Attempt*-level usage is `EvalSample.model_usage` (`log/_log.py:508`), summarised at `:310`. Citation corrected in the row | Citation imprecision |
| 8 | § 3, required dependencies | "6" for `pydantic-evals` | Correct as a *direct* count, but one of the six is `pydantic-ai-slim==2.43.0`, itself requiring nine more (`genai-prices`, `griffelib`, `httpx2`, `opentelemetry-api`, `pydantic-graph`, `pydantic`, `anyio`, `typing-inspection`, and `exceptiongroup` below Python 3.11). Qualification added in § 3.1 | Citation imprecision |

Two further imprecisions were judged too small to alter the text, and are
recorded here instead. `ReportCase.metadata` is typed `MetadataT | None`, not
`MetadataT` (§ 2 table, § 5 row); `Score.metadata` is `dict[str, Any] | None`,
not `dict[str, Any]` (§ 2 table, § 8 row). Neither changes a rating. Separately,
the models-overview page names Ollama, vLLM, and Hugging Face but not LM Studio
(§ 2 table, Stage 7 local route); LM Studio appears in the Pydantic AI
documentation only in `docs/capabilities/thinking.md`. The capability claim
stands — any OpenAI-compatible endpoint works — but that page does not name it.

### 6.2 Claims verified exactly, no change

*Repository and package metadata.* Every figure in § 3 reproduced to the digit:
stars 2,756 / 19,891; forks 719 / 2,706; contributors 306 / 476; last push
2026-09-13 / 2026-09-12; `inspect-ai` 0.3.263 uploaded 2026-09-04 and
`pydantic-evals` 2.43.0 uploaded 2026-09-12; 241 releases since 2024-04-03 with
24 in the last 90 days, and 280 releases with exactly ten between 2026-08-27 and
2026-09-12; monthly downloads 5,874,032 / 9,296,385; `inspect_evals` 669 stars;
41 versus 6 direct required dependencies, with Inspect's list confirmed to
include `fastapi`, `uvicorn`, `boto3`, `aioboto3`, `s3fs`, `textual`, `tiktoken`,
and `debugpy`. Neither repository is archived, and neither is a fork.

*Licences.* MIT on both, at both sources. `inspect_ai`'s `LICENSE` reads
"Copyright (c) 2024 UK AI Security Institute"; `pydantic-ai`'s reads "Copyright
(c) Pydantic Services Inc. 2024 to present". Both governance descriptions in § 3
are exactly right. `inspect_ai` publishes **zero** GitHub Releases, confirming
the draft's note that its cadence is inferred from PyPI upload dates.

*Dependency conflicts against this repository.* Both confirmed. `inspect-ai`
0.3.263 requires `pydantic>=2.13.0`; `requirements-lock.txt:106` pins
`pydantic==2.12.5`, and `pydantic` is absent from `requirements.txt`, so it is
transitive as claimed. `pydantic-ai-slim`'s `google` extra requires
`google-genai>=2.18.0`; `requirements-lock.txt:37` pins `google-genai==1.71.0`
and `requirements.txt:8` reads `google-genai>=1.69.0  # Minimum for ServiceTier
(flex mode) support`.

*Inspect type signatures.* `MetricProtocol.__call__(self, scores:
list[SampleScore]) -> Value` at `src/inspect_ai/scorer/_metric.py:349–350`,
verbatim as quoted in § 2.1. `Value` at `:67–71` is exactly the three-arm union
given. `SampleScore` at `:245–272` carries `score`, `sample_id`,
`sample_metadata: dict[str, Any] | None`, `sample_metadata_as()`, and `scorer`.
`Score.value: Value` at `:120`. `Sample.metadata` and `metadata_as()` at
`dataset/_dataset.py:88` and `:91`. `GenerateConfig.response_schema:
ResponseSchema | None` at `model/_generate_config.py:318`, with `ResponseSchema`
at `:20`.

*Inspect § 9 and § 8.3 mechanisms.* `grouped(metric, group_key, *, all=...,
all_label="all", ...)` at `scorer/_metrics/grouped.py:15–23`, raising if a sample
lacks the group key, and returning the group mapping plus the `all` rollup at
`:105`. `stderr(to_float=..., cluster: str | None = None)` at
`scorer/_metrics/std.py:122–124`, with a documented finite-cluster correction at
`:86–99`. Both are exported from `inspect_ai.scorer`.

*Inspect command-line options.* All present in `src/inspect_ai/_cli/eval.py`:
`--epochs` (:509), `--max-retries` (:543), `--attempt-timeout` (:552),
`--cost-limit` (:612), `--model-cost-config` (:618), `--fail-on-error` (:636),
`--retry-on-error` (:660), and `--run-config` (:311). The `inspect log`
subcommands `list` (with `--status`), `dump`, `convert`, `schema`,
`export-config`, and `recover` are all present in `_cli/log.py`. The log
`status: EvalStatus` field is at `log/_log.py:1228`, with `EvalStatus =
Literal["started", "success", "cancelled", "error"]` at `:60`. Per-sample
`total_time` and `working_time` at `:527–530` confirm the § 10 latency row.

*The export-config round-trip.* Confirmed verbatim from the command's own
docstring (`_cli/log.py:304–313`): "Reads LOG_FILE and writes a YAML (or JSON)
file that can be passed directly to 'inspect eval --run-config' to reproduce the
run". The docstring's worked example redirects `inspect log export-config
logs/my_run.eval` into `run.yaml`, then runs `inspect eval --run-config
run.yaml`. The `--run-config` help text at `eval.py:314` confirms the file
carries task, model, model roles, generate config, solver, and eval config.

*The `.eval` default.* `CHANGELOG.md:3135–3137`: "## v0.3.46 (12 November 2024)
— eval is now the default log format (use `--log-format=json` to use old
format)." Exactly as claimed, version and all.

*Pydantic AI evals types.* `ReportEvaluator.evaluate(ctx: ReportEvaluatorContext)
-> ReportAnalysis | list[ReportAnalysis] | Awaitable[...]` at
`evaluators/report_evaluator.py:40–54`, with `ReportEvaluatorContext.report:
EvaluationReport` at `:33`. `ReportAnalysis = Annotated[ConfusionMatrix |
PrecisionRecall | ScalarResult | TableResult | LinePlot, Discriminator('type')]`
at `reporting/analyses.py:127–130` — all five members present as claimed.
`ReportCase` at `reporting/__init__.py:87–119` exposes `metadata`, `metrics`,
`attributes`, `scores`, `labels`, `assertions`, `task_duration`,
`total_duration`, and `source_case_name` (documented in-source as "the
aggregation key for multi-run experiments"), confirming the § 10 repeated-epochs
row. `ReportCaseFailure` at `:124–148` carries `error_message` and
`error_stacktrace` and nothing else, so "message and stacktrace only" is exact.
`ReportCaseGroup` at `:156`. `EvaluatorOutput = EvaluationScalar |
EvaluationReason | Mapping[str, EvaluationScalar | EvaluationReason]` at
`evaluators/evaluator.py:49`. `set_eval_attribute` and `increment_eval_metric`
are both exported from `pydantic_evals/__init__.py:9`. `Dataset(BaseModel,
Generic[InputsT, OutputT, MetadataT])` at `dataset.py:177`, with
`to_file(..., schema_path=DEFAULT_SCHEMA_PATH_TEMPLATE, ...)` at `:747–781`
writing the JSON schema alongside the dataset. `evaluate(..., retry_task:
RetryConfig | None, retry_evaluators: RetryConfig | None, ..., repeat: int = 1)`
at `:288–292`.

*The log-format gap — the draft's largest single claim, and it holds.*
`EvaluationReport` (`reporting/__init__.py:317`) exposes `case_groups()`,
`averages()`, and `render()` and **no** `to_file`, `save`, or `write` method; the
only serialisation affordance is the `EvaluationReportAdapter` `TypeAdapter` at
`:726`, which is precisely "a Pydantic model you may serialise yourself". The
evals landing page confirms the Logfire routing: "Logfire serves as an
observability layer", and it names the "Logfire web interface for visualization,
comparison, and collaboration".

*Provider lists.* Inspect's providers page names vLLM, Ollama, Hugging Face,
SGLang, llama-cpp-python, TransformerLens, and `openai-api` — all seven as
claimed. Pydantic AI's models-overview page names `OpenAIChatModel`, Ollama,
vLLM, and a Hugging Face provider (see § 6.1 on LM Studio).

*Every cited URL resolves.* All 22 returned HTTP 200 under redirect-following:
the eight Inspect documentation pages plus the site root, the seven Pydantic
documentation pages, the two GitHub `blob` source links in § 2.1 (both at the
exact paths given), and the four repository links in § 3. The Inspect pages were
additionally cross-checked against `https://inspect.aisi.org.uk/sitemap.xml`
(95 entries, 26 of them API reference pages, which corroborates the "complete
API reference" claim).

**Injection watch, verification pass.** No page, API payload, source file, or
changelog entry retrieved during verification contained text addressed to an
agent, embedded instructions, false system notices, claimed date changes, or
authority or urgency framing. All retrieved content was treated as data. One
item is worth naming because it is the shape an injection would take: source
comments in `inspect_ai`'s `_metric.py` and `grouped.py` contain design
directives phrased imperatively and addressed to *maintainers* ("Own the empty
case", "Single source of truth for cluster identity"). These are ordinary code
comments about the code they sit beside, not instructions to a reader, and were
read as evidence about behaviour only.

## Changelog

### 2026-09-13 — Verified

**Trigger**: the `VERIFICATION PENDING` marker on the original publication.
Every checkable claim in §§ 2–4 was re-derived from primary sources in a separate
pass (GitHub API, PyPI, PyPI-Stats, raw repository source at `main` and at
release tags, and this repository's own requirement files). Verdict **PARTIAL
PASS**; the pending marker is replaced by the verdict, and the trail is recorded
in the new [§ 6](#6-verification-audit-trail).

Numerical and rating claims that moved:

| Claim | Before | After |
|---|---|---|
| § 10 attempt-level token usage, Pydantic AI evals | DIY **[unverified]**; divider Inspect | Supported (automatic); divider Tie |
| § 10 cost accounting, Pydantic AI evals | DIY **[unverified]**; divider Inspect | Supported (automatic); Inspect on enforcement only |
| § 3 "Open issues" | 305 / 871 | 206 / 615 open issues, plus 99 / 256 open PRs (the originals were `open_issues_count`, which includes PRs) |
| `ReportEvaluator` introduction | undated, flagged unverified | `pydantic-evals` 1.58.0, 2026-02-11 (PR #4243, commit `8a3cd8783`); `LinePlot` in 1.62.0, 2026-02-19 (PR #4356, commit `95d402e92`) |
| `logfire-api` inertness | **[unverified]** | Verified — a zero-dependency no-op shim |
| 9.3 M monthly downloads, provenance | **[inferred, not verified]** | Verified — the `evals` extra is in `pydantic-ai`'s default dependency set |

**What did NOT change**: the recommendation, in all four of its parts. The
Stage 5 neutrality decision is untouched, and Inspect AI remains the Stage 7
choice — the two corrected rows narrow the § 10 argument but do not reach the two
rows that actually decide it (the on-disk log format, and reproduction of a run
from a log artefact), both of which verified as stated. The § 3 maturity picture
is unchanged: every other figure in that table reproduced to the digit.
Section 1, § 2.1's core type-level finding, and § 4.1's questions 1 and 3 stand
as published. Question 2 of § 4.1 was narrowed, because the § 10 telemetry needs
only `opentelemetry-sdk`, not commercial Logfire.

One item remains unverified and is recorded as such in § 5: whether a large
dict-valued Inspect metric renders usefully in `inspect view`.

### 2026-09-13 — Original publication

Commissioned under § 13 of the benchmark plan after Brian recommended
investigating Pydantic AI evals alongside the provisional Inspect AI choice.
Initial state: a requirement-by-requirement comparison against plan §§ 5–10 and
Stage 7, a maturity and dependency assessment, and a recommendation to keep
Stage 5 framework-neutral while adopting Inspect AI at Stage 7 and Pydantic AI's
typed-model idiom for the § 5 metadata contract. No numerical claims from prior
revisions to diff.
