# Architecture Notes

## The dimensional model

`dbt_project/models/marts/` builds a standard star schema:

- `dim_customers` — one row per customer
- `dim_products` — one row per product
- `dim_date` — a date spine (3 years back through today), for consistent
  time-based joins and reporting even on dates with zero orders
- `fact_orders` — one row per order line item, with foreign keys to all
  three dimensions and the measures (`quantity`, `unit_price`, `line_total`)

This is the same modeling pattern (facts at a clear grain, conformed
dimensions) used in real data warehouses — chosen here over a single flat
"orders" table because it's what most analytics SQL and BI tools expect,
and because testing *relationships* between fact and dimension tables
(see below) is a meaningful data-quality check that a flat table can't
express.

## Why a staging layer between raw and marts

`models/staging/` does the minimal work of renaming and type-casting
raw columns before anything else touches the data. This exists so:

- Marts never reference raw source columns directly — if a source
  column gets renamed upstream, only the staging model needs to change.
- Each raw source gets exactly one staging model, so cleaning logic
  (e.g. a date cast) isn't duplicated across every mart that uses it.

## The 30 tests, and why that number matters more than it sounds

Running `dbt test` checks:

- **Uniqueness and not-null** on every primary key (staging and marts)
- **Referential integrity**: every `fact_orders.customer_id` actually
  exists in `dim_customers` (same for `product_id` -> `dim_products` and
  `order_date` -> `dim_date`) — `relationships` tests
- **Accepted values**: `status` is always one of `completed`/`cancelled`/`returned`
- **Two custom business-rule tests** (`dbt_project/tests/`): no negative
  order totals, no zero/negative quantities

The point isn't the count — it's that a broken upstream change (a bad
join, a source schema change, a bug in the generator) fails loudly in
`dbt test` instead of silently producing a warehouse that looks fine but
has orphaned foreign keys or impossible values. This is the same
instinct behind the resilience patterns in the other two projects in this
portfolio, applied to batch data instead of streaming data: catch bad
data before it reaches a dashboard or a stakeholder's report.

## Why DuckDB instead of Postgres/Snowflake/BigQuery

For a project meant to be cloned and run with zero setup, DuckDB removes
every piece of infrastructure a "real" warehouse needs (a running server,
credentials, a cloud account) while still being a genuine SQL analytical
database — not a toy. The dbt models, tests, and SQL are portable: moving
this to Snowflake/BigQuery/Postgres later is a `profiles.yml` change
(different adapter, different connection details), not a rewrite of any
model.

## Why two orchestration paths (script + Dagster)

`run_pipeline.py` is the simplest possible "make it work" path — three
function calls, no scheduler, no daemon, easy to read top to bottom.
`orchestration/pipeline.py` wraps the *same* three steps as Dagster
assets, adding:

- A visual dependency graph (useful the moment a pipeline has more than
  3 steps and a human needs to reason about it)
- Per-asset run history and metadata (row counts, dbt output) without
  adding custom logging
- A foundation for scheduling, retries, and partitioning if this grew
  into a daily/hourly job

Neither path duplicates pipeline logic — both call the exact same
`generate_all()`, `load_all()`, and dbt subprocess invocation.

## What would change for a real production source

- **Extract**: replace `data_generator/generate.py` with a real extractor
  (a database CDC tool like Debezium, an API client, or a bulk export) —
  everything downstream of "CSVs land in `raw_data/`" is unaffected.
- **Load**: for data too large to fit in a single DuckDB file, swap the
  `load/load_to_duckdb.py` target for a cloud warehouse and change
  `dbt_project/profiles.yml`'s adapter — the dbt models don't change.
- **Orchestration**: the Dagster job would move from manual materialization
  to a schedule (`@schedule` / `@sensor`) — e.g. "run every night after the
  upstream extract lands."
- **Incremental models**: at larger data volumes, `fact_orders` would
  become an `incremental` materialization (only processing new/changed
  rows each run) instead of a full rebuild every time.
