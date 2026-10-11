"""Loads the raw CSV extracts into a `raw` schema in DuckDB - the
"extract and load" half of ELT. dbt then owns all transformation logic
from this schema onward (see dbt_project/models/staging).
"""
from __future__ import annotations

from pathlib import Path

import duckdb

TABLES = ["customers", "products", "orders", "order_items"]


def load_all(raw_data_dir: Path, warehouse_path: Path) -> dict[str, int]:
    warehouse_path = Path(warehouse_path)
    warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    raw_data_dir = Path(raw_data_dir)

    con = duckdb.connect(str(warehouse_path))
    counts: dict[str, int] = {}
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")
        for table in TABLES:
            csv_path = raw_data_dir / f"{table}.csv"
            con.execute(
                f"CREATE OR REPLACE TABLE raw.{table} AS "
                f"SELECT * FROM read_csv_auto('{csv_path.as_posix()}', header=True)"
            )
            counts[table] = con.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchone()[0]
    finally:
        con.close()

    return counts
