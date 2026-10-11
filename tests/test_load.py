from pathlib import Path

from data_generator.generate import generate_all
from load.load_to_duckdb import load_all


def test_load_all_row_counts_match_generated_data(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    warehouse_path = tmp_path / "warehouse.duckdb"

    generated_counts = generate_all(raw_dir, n_customers=20, n_products=10, n_orders=30, seed=1)
    loaded_counts = load_all(raw_dir, warehouse_path)

    assert loaded_counts == generated_counts


def test_load_all_creates_warehouse_file(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    warehouse_path = tmp_path / "sub" / "warehouse.duckdb"

    generate_all(raw_dir, n_customers=5, n_products=5, n_orders=5, seed=1)
    load_all(raw_dir, warehouse_path)

    assert warehouse_path.exists()


def test_load_all_is_idempotent_on_rerun(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    warehouse_path = tmp_path / "warehouse.duckdb"

    generate_all(raw_dir, n_customers=5, n_products=5, n_orders=5, seed=1)
    first = load_all(raw_dir, warehouse_path)
    second = load_all(raw_dir, warehouse_path)

    assert first == second
