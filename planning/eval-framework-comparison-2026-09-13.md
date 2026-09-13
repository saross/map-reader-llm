# Evaluation framework comparison — Inspect AI versus Pydantic AI evals

> **Last revised**: 2026-09-13 (original publication). See [§ Changelog](#changelog) for revision history.

⚠ VERIFICATION PENDING

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
| § 10 attempt-level token usage | **Native** — the log's `stats` records model usage | DIY — `ReportCase.metrics` is populated by *our* `increment_eval_metric` calls **[unverified whether Pydantic AI's `genai-prices`-derived usage reaches a report case automatically]** | Inspect |
| § 10 cost accounting | **Native** — `--model-cost-config`, `--cost-limit` | DIY **[unverified]** | Inspect |
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
| Open issues | 305 | 871 |
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
framework*; the 9.3 million monthly `pydantic-evals` downloads almost certainly
reflect its inclusion in `pydantic-ai`'s default extras rather than independent
adoption of the evals layer **[inferred, not verified]**. Its `2.x` version is a
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
an isolated environment. Pydantic AI evals is far lighter, and `logfire-api` is
intended as a no-op shim when Logfire is absent, so the light footprint is
probably real rather than nominal; I did not verify the shim's behaviour
**[unverified]**.

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
2. **Stage 7 uses Inspect AI**, for § 10 (usage, cost, retry policy, failure
   accounting, completed-run validation — all native rather than DIY), for the
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
   local and file-based?** Much of `pydantic-evals`' experiment-comparison story
   routes through Logfire. A file-only constraint costs Pydantic AI evals a large
   part of its § 10 answer.
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

Explicitly **not** verified, and flagged in place above: whether Pydantic AI's
token usage and `genai-prices` cost data reach `ReportCase` without our code
doing it; whether `logfire-api` is truly inert without Logfire; whether a large
dict-valued Inspect metric renders usefully in `inspect view`; the date
`ReportEvaluator` was introduced — the documentation does not say, which matters
because a very recent feature is a thinner guarantee than a mature one; and
whether the 9.3 million monthly `pydantic-evals` downloads represent independent
use. Nothing here was tested by installing or running either package, so every
"Supported" rating is a documentation-level judgement, not an empirical one.

I searched both projects' documentation sites, repositories, and PyPI metadata.
I did not find, in either framework: exemplar-set hashing (§ 6), built-in
multiplicity correction or leaderboard tier formation (§ 8.3), or any cross-run
paired-permutation facility. Those are ours to build under every scenario.

**Injection watch**: no fetched page or API payload contained text addressed to
an agent, instructions, false system notices, or urgency framing. All retrieved
content was treated as data.

## Changelog

### 2026-09-13 — Original publication

Commissioned under § 13 of the benchmark plan after Brian recommended
investigating Pydantic AI evals alongside the provisional Inspect AI choice.
Initial state: a requirement-by-requirement comparison against plan §§ 5–10 and
Stage 7, a maturity and dependency assessment, and a recommendation to keep
Stage 5 framework-neutral while adopting Inspect AI at Stage 7 and Pydantic AI's
typed-model idiom for the § 5 metadata contract. No numerical claims from prior
revisions to diff.
