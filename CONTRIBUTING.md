# Contributing

Thanks for taking a look at this project. It started as a personal demo,
but issues and pull requests are genuinely welcome.

## Getting set up

```bash
git clone https://github.com/mallajaswanthkumar10/retail-analytics-elt.git
cd retail-analytics-elt
python -m venv .venv && source .venv/bin/activate   # .venv\Scripts\activate on Windows
make install
```

Run the whole pipeline end to end (generate data -> load DuckDB -> dbt run
-> dbt test) with:

```bash
python run_pipeline.py
```

## Before opening a PR

- Unit tests: `make test` (or `pytest tests/ -v`)
- dbt data-quality tests: `python run_pipeline.py` (runs all 30 of them)
- Lint: `flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics`
- All three of these run in CI on every push/PR - a green run there
  confirms you're good to go.

## What's especially welcome

- New dbt tests or models (`dbt_project/models/`) - more data-quality
  coverage is always useful
- Dagster asset improvements (`orchestration/pipeline.py`)
- Dashboard panels (`dashboard/app.py`)
- Doc fixes in the README or `docs/ARCHITECTURE.md`

No change is too small. A draft PR is a perfectly good way to start a
conversation - you don't need to open an issue first.
