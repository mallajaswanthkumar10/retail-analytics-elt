"""Generates a synthetic e-commerce dataset (customers, products, orders,
order_items) standing in for a real OLTP source extract. Deterministic
given the same seed, so re-running the pipeline produces a stable demo
dataset rather than different numbers every time.
"""
from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

CATEGORIES = ["Electronics", "Home & Kitchen", "Books", "Clothing", "Sports", "Toys"]
ORDER_STATUSES = ["completed", "completed", "completed", "completed", "cancelled", "returned"]


def generate_customers(n: int, seed: int) -> list[dict]:
    fake = Faker()
    Faker.seed(seed)
    rng = random.Random(seed)

    customers = []
    for i in range(1, n + 1):
        signup_date = date.today() - timedelta(days=rng.randint(30, 900))
        customers.append(
            {
                "customer_id": i,
                "name": fake.name(),
                "email": fake.unique.email(),
                "signup_date": signup_date.isoformat(),
                "country": fake.country(),
            }
        )
    return customers


def generate_products(n: int, seed: int) -> list[dict]:
    fake = Faker()
    Faker.seed(seed + 1)
    rng = random.Random(seed + 1)

    products = []
    for i in range(1, n + 1):
        products.append(
            {
                "product_id": i,
                "name": fake.catch_phrase(),
                "category": rng.choice(CATEGORIES),
                "unit_price": round(rng.uniform(5.0, 500.0), 2),
            }
        )
    return products


def generate_orders_and_items(
    customers: list[dict], products: list[dict], n_orders: int, seed: int
) -> tuple[list[dict], list[dict]]:
    rng = random.Random(seed + 2)

    orders = []
    order_items = []
    item_id = 1

    for order_id in range(1, n_orders + 1):
        customer = rng.choice(customers)
        order_date = date.today() - timedelta(days=rng.randint(0, 730))
        orders.append(
            {
                "order_id": order_id,
                "customer_id": customer["customer_id"],
                "order_date": order_date.isoformat(),
                "status": rng.choice(ORDER_STATUSES),
            }
        )

        for _ in range(rng.randint(1, 5)):
            product = rng.choice(products)
            order_items.append(
                {
                    "order_item_id": item_id,
                    "order_id": order_id,
                    "product_id": product["product_id"],
                    "quantity": rng.randint(1, 4),
                    "unit_price": product["unit_price"],
                }
            )
            item_id += 1

    return orders, order_items


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def generate_all(raw_data_dir: Path, n_customers: int, n_products: int, n_orders: int, seed: int) -> dict[str, int]:
    customers = generate_customers(n_customers, seed)
    products = generate_products(n_products, seed)
    orders, order_items = generate_orders_and_items(customers, products, n_orders, seed)

    raw_data_dir = Path(raw_data_dir)
    _write_csv(raw_data_dir / "customers.csv", customers)
    _write_csv(raw_data_dir / "products.csv", products)
    _write_csv(raw_data_dir / "orders.csv", orders)
    _write_csv(raw_data_dir / "order_items.csv", order_items)

    return {
        "customers": len(customers),
        "products": len(products),
        "orders": len(orders),
        "order_items": len(order_items),
    }
