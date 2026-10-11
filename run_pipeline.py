"""Runs the full ELT pipeline end to end:
    1. generate synthetic raw data
    2. load it into DuckDB
    3. run dbt transformations, then dbt tests

This is the simple, always-works path - no orchestrator required. See
orchestration/pipeline.py for the same three steps wired up as a Dagster
job, for when you want scheduling/observability on top.

Usage:
    python run_pipeline.py
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

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

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("run_pipeline")


def _dbt_executable() -> str:
    """Resolve the `dbt` console script installed alongside this venv's
    Python, rather than relying on PATH - works regardless of whether the
    venv is "activated" in the calling shell."""
    venv_bin = Path(sys.executable).parent
    candidate = venv_bin / ("dbt.exe" if os.name == "nt" else "dbt")
    return str(candidate) if candidate.exists() else "dbt"


def run_dbt(command: list[str]) -> None:
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
    result = subprocess.run(args, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"dbt {' '.join(command)} failed with exit code {result.returncode}")


def main() -> None:
    log.info("Step 1/3: generating synthetic raw data")
    counts = generate_all(RAW_DATA_DIR, N_CUSTOMERS, N_PRODUCTS, N_ORDERS, RANDOM_SEED)
    log.info("generated: %s", counts)

    log.info("Step 2/3: loading raw data into DuckDB")
    load_counts = load_all(RAW_DATA_DIR, WAREHOUSE_PATH)
    log.info("loaded: %s", load_counts)

    log.info("Step 3/3: running dbt transformations")
    run_dbt(["run"])
    log.info("running dbt tests")
    run_dbt(["test"])

    log.info("Pipeline complete. Warehouse at %s", WAREHOUSE_PATH)


if __name__ == "__main__":
    main()
