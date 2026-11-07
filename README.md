<img src="./banner.png" width="100%" alt="Seinokojii — AI Engineer">

<br>

I am moving from analytics engineering into AI engineering, in the open. The rule stays
the same as before: if a change cannot be measured, it is not an improvement yet. So every
model call logs its tokens, latency and cost, and every project ships with evals that can
fail the build.

<br>

<a href="https://github.com/Seinokojii/ai-engineer-roadmap"><img src="./assets/pipeline.f1761370.svg" width="100%" alt="What I am building: ai-engineer-roadmap. Data, retrieval, a local-first model, schema checks and guardrails, then serving through an API and Telegram. Tokens, latency and cost are logged on every call, and evals run on every change."></a>

### Recent work

<!-- recent starts -->
- [Day 003-004 aieng.text and project exceptions](https://github.com/Seinokojii/ai-engineer-roadmap/commit/520099ad01c86e2b1cdfc3d00aee894f102dcbc0) &nbsp;<sub>07 Nov 2026</sub>
- [Day 001-002 environment lesson](https://github.com/Seinokojii/ai-engineer-roadmap/commit/ac7701a54cd7b7e744c5a2624e00ec18ebc29e4f) &nbsp;<sub>07 Nov 2026</sub>
<!-- recent ends -->

<br>

<img src="./assets/journey.cc78672c.svg" width="100%" alt="The way through: foundations now; then evals, retrieval and RAG, tools and agents with MCP, production, and middle-level topics.">

<details>
<summary>The full plan, part by part</summary>

<br>

| Block | Days | Covered |
|---|---|---|
| **Foundations** | Days 1-30 | Python for AI code, tokens and sampling, a thin client over local and hosted models, structured output, a review classifier |
| **Evals** | Days 31-50 | Metrics and datasets, LLM-as-judge checked against human labels, error analysis, evals in CI — and evalkit, used by everything after it |
| **Retrieval and RAG** | Days 51-85 | Embeddings, chunking, pgvector, hybrid search and reranking, retrieval and faithfulness evals, incremental indexing |
| **Tools, agents, MCP** | Days 86-110 | Tool calling, an agent loop written by hand, workflows versus agents, an MCP server, agent evals, human-in-the-loop |
| **Production** | Days 111-145 | FastAPI, Docker, fallbacks and rate limits, tracing, caching, cost routing, prompt-injection tests, deploy with an eval gate |
| **Middle level** | Days 146-180 | Quantised local inference, LoRA against a prompting baseline, multimodal extraction, five written system designs |

Three projects instead of ten: a review classifier, an eval harness every later part uses,
and one retrieval product that grows from search to an agent to a deployed service.

</details>

<br>

<img src="./assets/stack.88cedbc6.svg" width="100%" alt="Stack: Python 3.12, uv, pytest, ruff; Ollama locally first and hosted free tiers second; pydantic schemas; evalkit; PostgreSQL, pgvector, full-text search, reranking; tool calling, an own agent loop, MCP; FastAPI, Docker, OpenTelemetry, Langfuse; background in SQL, dbt and Dagster.">

<br>

<img src="./assets/activity.e1a29e49.svg" width="100%" alt="Contribution activity over the last year">

<br>

Before this: a full analytics engineering pipeline — [live dashboard](https://seinokojii.github.io/analytics-engineer-roadmap/) ·
[dbt docs](https://seinokojii.github.io/analytics-engineer-roadmap/dbt/) · [repository](https://github.com/Seinokojii/analytics-engineer-roadmap).

<sub>AI・エンジニア　·　<a href="https://github.com/Seinokojii?tab=repositories">repositories</a>　·　this page rebuilds itself nightly from the GitHub API — <a href="./assets/build.py">assets/build.py</a></sub>
