<img src="./banner.png" width="100%" alt="Seinokojii — Analytics Engineer">

<br>

I build the layer between raw data and the numbers people actually trust. Ingestion,
modelling, tests, orchestration, and a BI surface that does not lie — assembled in the
open, one working piece at a time, and reproducible from a clean checkout.

<br>

<a href="https://github.com/Seinokojii/analytics-engineer-roadmap"><img src="./assets/pipeline.da344807.svg" width="100%" alt="Current work: analytics-engineer-roadmap. Source to raw to staging to marts to BI, orchestrated by Dagster, partitioned by day, with 30 tests in three layers and CI on every pull request."></a>

<br>

<img src="./assets/quality.c532d59c.svg" width="100%" alt="Four layers of data checks: dbt core tests ask whether a row is valid, dbt-expectations whether a value is plausible, Elementary whether today looks like yesterday, and Dagster asset checks whether downstream should run at all.">

<br>

<img src="./assets/stack.2be78d3c.svg" width="100%" alt="Stack: Snowflake, DuckDB, PostgreSQL; dbt; Dagster; Airbyte; dbt-expectations, Elementary, pytest; dbt Semantic Layer, MetricFlow, Lightdash; FastAPI, SQLAlchemy; Docker, Linux, GitHub Actions.">

<br>

<img src="./assets/journey.852a78fd.svg" width="100%" alt="Progress through the roadmap: foundations, dbt end to end, orchestration and cloud are done; Snowflake architecture is current; semantics and BI come next.">

<br>

<img src="./assets/activity.03669c8b.svg" width="100%" alt="Contribution activity over the last year">

<br>

A test suite that has never failed is an unverified test suite, so the roadmap repository
corrupts its own warehouse on purpose, asserts the tests go red, and restores it.

<sub>アナリティクス・エンジニア　·　<a href="https://github.com/Seinokojii?tab=repositories">repositories</a>　·　panels rebuilt nightly from the GitHub API by <a href="./assets/build.py">assets/build.py</a></sub>
