"""Dagster version of the same ELT pipeline as run_pipeline.py - adds a
visual asset graph, run history, and per-asset observability on top of
the exact same functions the plain-Python script calls (no logic is
duplicated between the two).

Run:
    dagster dev -f orchestration/pipeline.py
then open http://localhost:3000 and materialize all assets.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dagster import AssetExecutionContext, Definitions, MaterializeResult, MetadataValue, asset

from config import (
    DBT_PROFILES_DIR,
    DBT_PROJECT_DIR,
    N_CUSTOMERS,
    N_ORDERS,
    N_PRODUCTS,
    RANDOM_SEED,
    RAW_DATA_DIR,
    WAREHOUSE_PATH,
)
from data_generator.generate import generate_all
from load.load_to_duckdb import load_all


def _dbt_executable() -> str:
    venv_bin = Path(sys.executable).parent
    candidate = venv_bin / ("dbt.exe" if os.name == "nt" else "dbt")
    return str(candidate) if candidate.exists() else "dbt"


def _run_dbt(command: list[str]) -> str:
    env = os.environ.copy()
    env["WAREHOUSE_PATH"] = str(WAREHOUSE_PATH)
    args = [
        _dbt_executable(),
        *command,
        "--project-dir",
        str(DBT_PROJECT_DIR),
        "--profiles-dir",
        str(DBT_PROFILES_DIR),
    ]
    result = subprocess.run(args, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"dbt {' '.join(command)} failed:\n{result.stdout}\n{result.stderr}")
    return result.stdout


@asset
def raw_data() -> MaterializeResult:
    counts = generate_all(RAW_DATA_DIR, N_CUSTOMERS, N_PRODUCTS, N_ORDERS, RANDOM_SEED)
    return MaterializeResult(metadata={k: MetadataValue.int(v) for k, v in counts.items()})


@asset(deps=[raw_data])
def warehouse_raw_tables() -> MaterializeResult:
    counts = load_all(RAW_DATA_DIR, WAREHOUSE_PATH)
    return MaterializeResult(metadata={k: MetadataValue.int(v) for k, v in counts.items()})


@asset(deps=[warehouse_raw_tables])
def dbt_models() -> MaterializeResult:
    output = _run_dbt(["run"])
    return MaterializeResult(metadata={"dbt_run_output": MetadataValue.text(output[-2000:])})


@asset(deps=[dbt_models])
def dbt_tests() -> MaterializeResult:
    output = _run_dbt(["test"])
    return MaterializeResult(metadata={"dbt_test_output": MetadataValue.text(output[-2000:])})


defs = Definitions(assets=[raw_data, warehouse_raw_tables, dbt_models, dbt_tests])
