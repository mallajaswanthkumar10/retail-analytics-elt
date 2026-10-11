# Retail Analytics ELT Pipeline

A batch ELT pipeline for e-commerce data: synthetic orders get loaded into
a local warehouse, transformed into a proper dimensional model with
**dbt**, tested automatically, and visualized on a dashboard. Orchestrated
two ways — a simple script, and a **Dagster** asset graph with a visual
UI.

No cloud account, no Docker, no API key needed — everything runs locally
with DuckDB as the warehouse. This is the "classic" batch analytics
engineering stack (dbt + a warehouse + orchestration + testing) that most
data engineering job postings are actually looking for day to day.

## How it works

```
  synthetic e-commerce data generator
  (customers, products, orders, order_items)
                |
                v
     raw_data/*.csv  ("extract")
                |
                v
     loaded into DuckDB, schema "raw"  ("load")
                |
                v
     dbt transforms + tests  ("transform")
       staging models (clean + rename)
                |
       dimensional marts:
       dim_customers, dim_products, dim_date, fact_orders
                |
                v
     Streamlit dashboard reads the marts directly
```

Both the plain-Python script and the Dagster job run these exact same
three steps (generate -> load -> dbt run/test) - Dagster just adds a
visual graph, run history, and per-step metadata on top.

## What's in this project

| What it does | Where to find it |
|---|---|
| Generates synthetic order data | `data_generator/generate.py` |
| Loads raw data into DuckDB | `load/load_to_duckdb.py` |
| Cleans + renames raw data | `dbt_project/models/staging/` |
| Builds the dimensional model | `dbt_project/models/marts/` |
| Data quality tests (30 of them) | `dbt_project/models/**/*.yml` + `dbt_project/tests/` |
| Simple run-it-yourself pipeline | `run_pipeline.py` |
| Dagster orchestration (visual UI) | `orchestration/pipeline.py` |
| Analytics dashboard | `dashboard/app.py` |
| Automated tests | `tests/` |
| Deeper design notes | `docs/ARCHITECTURE.md` |

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the whole pipeline

```bash
python run_pipeline.py
```

This generates ~500 customers, ~60 products, and ~2,000 orders, loads them
into `data/warehouse.duckdb`, runs all 8 dbt models, and runs all 30 data
quality tests. Takes about 10 seconds.

Then view the results:

```bash
streamlit run dashboard/app.py
```

## Or run it through Dagster instead

```bash
dagster dev -f orchestration/pipeline.py
```

Open http://localhost:3000, find the asset graph, and click "Materialize
all" to run the same pipeline with a visual UI and run history.

## Exploring the warehouse directly

```bash
python -c "
import duckdb
con = duckdb.connect('data/warehouse.duckdb', read_only=True)
print(con.execute('select * from main.fact_orders limit 5').fetchdf())
"
```

Or point any SQL tool that supports DuckDB at `data/warehouse.duckdb`.

## Running the tests

The data generator and loader are tested directly (determinism, row
counts, referential consistency):

```bash
pytest tests/ -v
```

dbt's own 30 data quality tests (uniqueness, not-null, referential
integrity, custom business rules) run as part of the pipeline itself —
`python run_pipeline.py` or the Dagster `dbt_tests` asset.

## Good to know

- **Data is synthetic but deterministic.** The same seed always produces
  the same dataset, so re-running the pipeline gives reproducible numbers
  — useful for demos, less useful if you want different numbers each
  time (change `RANDOM_SEED` in `config.py`).
- **No `dbt deps` / package installs.** The date dimension is built with
  DuckDB's native `generate_series` instead of a `dbt_utils` macro, so
  there's no extra network dependency to set up the project.
- **DuckDB is single-writer.** Don't run `dbt run` and the dashboard's
  write path at the same time against the same file — the dashboard
  already opens the warehouse read-only to avoid this, but a second `dbt
  run` while one is in progress will conflict.

More on the dimensional model, why dbt + DuckDB, and how this would
change for a production source: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## License

MIT — see [LICENSE](LICENSE).
