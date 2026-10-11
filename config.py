"""Paths and settings shared across the generator, loader, dbt profile,
orchestration, and dashboard."""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()

RAW_DATA_DIR = Path(os.environ.get("RAW_DATA_DIR", PROJECT_ROOT / "raw_data"))
WAREHOUSE_PATH = Path(os.environ.get("WAREHOUSE_PATH", PROJECT_ROOT / "data" / "warehouse.duckdb"))

DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_project"
DBT_PROFILES_DIR = PROJECT_ROOT / "dbt_project"

N_CUSTOMERS = int(os.environ.get("N_CUSTOMERS", "500"))
N_PRODUCTS = int(os.environ.get("N_PRODUCTS", "60"))
N_ORDERS = int(os.environ.get("N_ORDERS", "2000"))

RANDOM_SEED = int(os.environ.get("RANDOM_SEED", "42"))
